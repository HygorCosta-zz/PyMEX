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
import pandas as pd
import multiprocessing as mp
from string import Template
import os
from subprocess import Popen, check_call
from pathlib import Path
import numpy as np
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

    def __init__(self, controls, tpl, restore_file, *args):
        super().__init__(controls, *args)
        self.prod = []
        self.tpl = tpl
        self.restore_file = restore_file
        self.basename = self.cmgfile(create_name())
        self.npv = []
        self.__call__()

    def _control_time(self):
        """ Define control time."""
        time_conc = self.res_param['time_concession']
        times = np.linspace(0, time_conc,
                            int(time_conc / 30) + 1,
                            dtype=int)
        control_time = np.round(self.time_steps()[:-1])
        id_sort = np.searchsorted(times, control_time)
        times = np.unique(np.insert(times, id_sort, control_time))
        return control_time, times

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
            prod_values = map(str, np.round(well_prod, 4))
            return ' '.join(prod_values)

        def write_alter(day, control, nb_prod, nb_inj):
            """ Write the ALTER element."""
            div = '**' + '-' * 30
            if day == 0:
                time = '**TIME ' + str(day)
            else:
                time = '*TIME ' + str(day)
            prod_name = alter_wells("PROD", nb_prod)
            prod_rate = wells_rate(control[: nb_prod])
            inj_name = alter_wells("INJECT", nb_inj)
            inj_rate = wells_rate(control[nb_prod:])

            lines = [div, time, div, prod_name, prod_rate,
                     div, inj_name, inj_rate, div, '\n']
            return '\n'.join(lines)

        control_time, times = self._control_time()
        count = 0
        ctime = control_time[count]

        for time_step in times[:-1]:
            if count < len(control_time) and \
                    ctime == time_step:
                control = self.modif_controls[count]
                content_text += write_alter(ctime, control,
                                            nb_prod, nb_inj)
                count += 1
                if count < len(control_time):
                    ctime = control_time[count]
            else:
                time = '*TIME ' + str(time_step) + '\n'
                content_text += time

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

        tpl_name = os.path.join(self.run_path, self.tpl)
        with open(tpl_name, "r") as tpl_file, \
                open(self.basename['dat'], "w") as dat:
            template_content = tpl_file.read()

            if self.controls:
                operation_content = ''.join(self.include_operation())
                stop = [f'*TIME {time_conc}', "*STOP"]
                operation_content += '\n'.join(stop)

                template_content = re.sub(r"[\W][\W]WELL_INC",
                                          operation_content,
                                          template_content)
            dat.write(template_content)

    def rwd_file(self):
        """create *.rwd (output conditions) from report.tmpl. """
        tpl_report = os.path.join(self.res_param['path'],
                                  self.res_param['tpl_report'])
        with open(tpl_report, "r") as tmpl, \
                open(self.basename['rwd'], "w") as rwd:
            tpl = Template(tmpl.read())
            content = tpl.substitute(IRFFILE=self.basename['irf'])
            rwd.write(content)

    def _colum_names(self):
        """ Define the range of columns from rwo file."""
        if self.res_param['wells_resul']:
            nprod = self.res_param['nprod']
            cum_op = [f"cum_op_p{i + 1}" for i in range(nprod)]
            cum_or = [f"cum_or_p{i + 1}" for i in range(nprod)]
            self.prod.columns = ['time'] + cum_op + cum_or
        else:
            col_name = ['cum_op', 'cum_wp', 'cum_gp', 'cum_wi',
                        'oil_rate', 'wat_rate', 'liq_rate',
                        'pressure']
            self.prod.columns = col_name

    def get_production(self, log, procedure):
        """ Get production for results."""
        if procedure.returncode == 0:
            imex_path = "/cmg/br/2018.10/linux_x64/exe/report.exe"
            check_call([imex_path, "-f", self.basename['rwd'], "-o",
                        self.basename['rwo']], stdout=log,
                       cwd=str(self.run_path))
            try:
                with open(self.basename['rwo']) as rwo:
                    self.prod = pd.read_csv(rwo,
                                            sep='\t',
                                            index_col=False,
                                            header=6)
            except StopIteration as err:
                print("StopIteration error: Failed in Imex run.")
                print(f"Verify {self.basename['log']}")
                raise err
            self.prod = self.prod.dropna(axis=1, how='all')
            self._colum_names()
        else:
            # IMEX has failed, receive None
            self.prod = None

    def run_imex(self):
        """ call IMEX + Results Report. """
        # environ['CMG_HOME'] = '/cmg'

        with open(self.basename['log'], "w") as log:
            dat_path = self.basename['dat']
            path = ['/cmg/RunSim.sh', 'imex', '2018.10', dat_path]
            procedure = Popen(path, stdout=log, cwd=str(self.run_path))
            procedure.wait()
            self.get_production(log, procedure)

    def restore_run(self):
        """ Restart the IMEX run."""
        with open(self.basename['rwo']) as rwo:
            self.prod = pd.read_csv(rwo,
                                    sep='\t',
                                    index_col=False,
                                    header=6)
        self.prod = self.prod.dropna(axis=1, how='all')
        self._colum_names()

    def _dif_production(self):
        """ Calculate the increase amount by time step."""
        dif_volume = []
        product = self.prod[['cum_op', 'cum_wp',
                             'cum_gp', 'cum_wi']].to_numpy()
        for volume in product.T:
            dif_volume.append(np.diff(volume))
        return dif_volume

    def cash_flow(self):
        """ Return the cash flow from production."""
        oil_price, water_prod_cost, water_inj_cost, _\
            = self.res_param["prices"]

        dif_volume = self._dif_production()
        vol_oil_prod = dif_volume[0]
        vol_water_prod = dif_volume[1]
        vol_water_inj = dif_volume[3]

        # Multiply by each price
        revenue_oil = vol_oil_prod * oil_price
        cost_water_prod = vol_water_prod * water_prod_cost
        cost_water_inj = vol_water_inj * water_inj_cost

        # Cash flow
        cash_flows = revenue_oil - cost_water_prod - cost_water_inj

        return np.insert(cash_flows, 0, 0)

    def net_present_value(self):
        """ Calculate the net present value of the \
            reservoir production"""
        discount_rate = self.res_param["prices"][-1]

        # Convert to periodic rate
        periodic_rate = ((1 + discount_rate) ** (1 / 365)) - 1

        # Create the cash flow (x 10^6) (Format of the numpy.npv())
        cash_flows = self.cash_flow()

        # Discount tax
        time = self.prod['time'].to_numpy()
        tax = 1 / np.power((1 + periodic_rate), time)
        npv_value = np.sum(np.multiply(cash_flows, tax.T))
        self.npv = npv_value * (-1e-6)

    def __call__(self):
        """
        Run Imex.
        """
        if not self.restore_file:
            # Verify if the Run_Path exist
            Path(self.run_path).mkdir(parents=True, exist_ok=True)

            # Write the well controls in data file
            self.create_well_operation()

            # Create .rwd file
            self.rwd_file()

            # Run Imex + Results Report
            self.run_imex()

            # Evaluate the net present value
            if not self.res_param['wells_resul']:
                self.net_present_value()

            # Remove all files create in Run Imex
            self.clean_up()
        else:
            self.restore_run()

    def clean_up(self):
        """ Delet imex auxiliar files."""
        for _, filename in self.basename.items():
            try:
                os.remove(filename)
            except OSError:
                print(f"File {filename} could not be removed,\
                      check if it's yet open.")
