"""
# -*- coding: utf8 -*-
# Copyright (c) 2019 Hygor Costa
#
# This file is part of Py_IMEX.
#
#
# You should have received a copy of the GNU General Public License
# along with HUM.  If not, see <http://www.gnu.org/licenses/>.
#
# Created: Jul 2019
# Author: Hygor Costa
"""
import re
import multiprocessing as mp
from string import Template
from os import remove, environ
from subprocess import Popen, check_call
from pathlib import Path
import numpy as np
import numpy_financial as npf
from .ImexTools import ImexTools


def my_pid():
    """ Returns the relative pid of a pool
    process."""
    cur_proc = mp.current_process()
    if cur_proc._identity:
        return cur_proc._identity[0]
    return 0


def create_name():
    """ Create dat name for parallel
    run."""
    pid = my_pid()
    return f"rank{pid}"


class PyMEX(ImexTools):
    """
        Manipulate the files give in.
    """

    def __init__(self, controls, *args):
        super().__init__(controls, *args)
        self.restore_file = False
        self.basename = self.cmgfile(create_name())
        self.time = np.array([])
        self.production = np.array([])
        self.wells_rate = np.array([])
        self.average_pressure = np.array([])

    def include_operation(self):
        """ Print operation of the wells."""
        content_text = []
        nb_prod = self.res_param["nb_prod"]
        nb_inj = self.res_param["nb_inj"]

        def alter_wells(well_type, number):
            """ Create the wells names."""
            wells_name = [f"'{well_type}{i + 1}'" for i in range(number)]
            return ' '.join(['*ALTER'] + wells_name)

        def wells_rate(well_prod):
            """ Return the string of the wells rate."""
            prod_values = map(str, well_prod)
            return ' '.join(prod_values)

        for time_step, well_prod in zip(self.time_steps(),
                                        self.modif_controls):

            div = '**' + '-' * 30
            if time_step != 0:
                time = '*TIME ' + str(time_step)
            else:
                time = '**TIME ' + str(time_step)
            prod_name = alter_wells("PROD", nb_prod)
            prod_rate = wells_rate(well_prod[: nb_prod])
            inj_name = alter_wells("INJ", nb_inj)
            inj_rate = wells_rate(well_prod[nb_prod:])

            lines = [div, time, div, prod_name, prod_rate,
                     div, inj_name, inj_rate, div, '\n']
            content_text += '\n'.join(lines)

        return content_text

    def create_well_operation(self):
        """Create a include file (.inc) to be incorporated to the .dat.

        Wrap the design variables in separated control cycles
        if the problem is time variable,
        so the last list corresponds to these.
        new_controls = list(chunks(design_controls, npp + npi))
        """
        type_opera = self.res_param["type_opera"]
        time_conc = self.res_param["time_concession"]
        if type_opera == 0:  # full_capacity
            self.full_capacity()
        else:  # non - full - capacity
            pass

        # create *.dat from template
        tpl_name = self.file_to_open(self.res_param["template"])
        with open(tpl_name, "r") as tpl_file, \
                open(self.basename['dat'], "w") as dat:
            template_content = tpl_file.read()

            operation_content = ''.join(self.include_operation())
            stop = [f'*TIME {time_conc}', "*STOP"]
            operation_content += '\n'.join(stop)

            template_content = re.sub(r"[\W][\W]WELL_INC",
                                      operation_content, template_content)
            dat.write(template_content)

    def rwd_file(self):
        """create *.rwd (output conditions) from report.tmpl. """
        tpl_report = self.file_to_open("NewTemplateReport.tpl")
        with open(tpl_report, "r") as tmpl, \
                open(self.basename['rwd'], "w") as rwd:
            tpl = Template(tmpl.read())
            content = tpl.substitute(IRFFILE=self.basename['irf'])
            rwd.write(content)

    def get_production(self, log, procedure):
        """ Get production for results."""
        # columns in output spreadsheet (lexicographic order)
        id_range = range(0, 10)
        id_time = [0]  # 0 column
        id_prod = range(1, 5)  # 1, 2 e 3 columns
        id_rate = range(5, 9)  # 4, 5 e 6 columns
        id_press = [9]  # 7 columns
        if procedure.returncode == 0:
            # get oil rate SC for all 20 producer wells
            imex_path = "/cmg/br/2018.10/linux_x64/exe/report.exe"
            check_call([imex_path, "-f", self.basename['rwd'], "-o",
                        self.basename['rwo']], stdout=log,
                       cwd=str(self.run_path))
            content_rwo = np.loadtxt(
                self.basename['rwo'], skiprows=6, usecols=id_range)
            time = content_rwo[:, id_time]
            production = content_rwo[:, id_prod]
            wells_rate = content_rwo[:, id_rate]
            aver_press = content_rwo[:, id_press]
        else:
            # IMEX has failed, nullify production
            production = np.zeros([len(self.time_steps), len(id_prod)])
            wells_rate = np.zeros([len(self.time_steps), len(id_rate)])
            aver_press = np.zeros([len(self.time_steps), 1])
        return time, production, wells_rate, aver_press

    def run_imex(self):
        """ call IMEX + Results Report. """
        environ['CMG_HOME'] = '/cmg'

        with open(self.basename['log'], "w") as log:
            dat_path = str(self.workdir.joinpath(self.basename['dat']))
            path = ['/cmg/RunSim.sh', 'imex', '2018.10', dat_path]
            procedure = Popen(path, stdout=log, cwd=str(self.run_path))
            procedure.wait()
            return self.get_production(log, procedure)

    def restore_run(self):
        """ Restart the IMEX run."""
        # columns in output spreadsheet (lexicographic order)
        id_range = range(0, 10)
        id_time = [0]  # 0 column
        id_prod = range(1, 5)  # 1, 2 e 3 columns
        id_rate = range(5, 9)  # 4, 5 e 6 columns
        id_press = [9]  # 7 columns
        if self.restore_file:
            content_rwo = np.loadtxt(
                self.basename['rwo'], skiprows=6, usecols=id_range)
            time = content_rwo[:, id_time]
            production = content_rwo[:, id_prod]
            wells_rate = content_rwo[:, id_rate]
            aver_press = content_rwo[:, id_press]
        else:
            # IMEX has failed, nullify production
            time = np.zeros([len(self.time_steps), len(id_time)])
            production = np.zeros([len(self.time_steps), len(id_prod)])
            wells_rate = np.zeros([len(self.time_steps), len(id_rate)])
            aver_press = np.zeros([len(self.time_steps), 1])
        return time, production, wells_rate, aver_press

    @ property
    def net_present_value(self):
        """ Calculate the net present value of the \
            reservoir production"""
        oil_price, water_prod_cost, water_inj_cost, discount_rate\
            = self.res_param["prices"]

        vol_oil_prod, vol_water_prod, _, vol_water_inj\
            = self.production.T

        # Multiply by each price
        revenue_oil = vol_oil_prod * oil_price
        cost_water_prod = vol_water_prod * water_prod_cost
        cost_water_inj = vol_water_inj * water_inj_cost

        # Create the cash flow (x 10^6) (Format of the numpy.npv())
        cash_flows = revenue_oil - cost_water_prod - cost_water_inj
        npv = npf.npv(discount_rate, cash_flows) * (-1) * 10 ** (-6)
        return npv

    def call_pymex(self):
        """

        :rtype: float
        """
        if not self.restore_file:
            # Verify if the Run_Path exist
            Path(self.run_path).mkdir(parents=True, exist_ok=True)

            # Write the well controls in data file
            self.create_well_operation()

            # Create .rwd file
            self.rwd_file()

            # Run Imex + Results Report
            self.time, self.production, self.wells_rate, \
                self.average_pressure = self.run_imex()

            # Remove all files create in Run Imex
            self.clean_up()
        else:
            self.time, self.production, self.wells_rate,\
                self.average_pressure = self.restore_run()

    @ property
    def report_resul(self):
        """ Return concatenate time, production, wells_rate,\
            average pressure"""
        return [self.time, self.production, self.wells_rate,
                self.average_pressure]

    def clean_up(self):
        """ Delet imex auxiliar files."""
        for _, filename in self.basename.items():
            try:
                remove(filename)
            except OSError:
                print(f"File {filename} could not be removed,\
                      check if it's yet open.")
