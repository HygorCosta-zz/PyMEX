"""Imex Tools.
# *- coding: utf8 -*-
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

from collections import namedtuple
from pathlib import Path
import os
import numpy as np


class ImexTools:
    """ Create tools for simulate the value of the well_controls in
    IMEX."""

    def __init__(self, well_controls, res_param):
        """
        Parameters
        ----------
        well_controls: array
            Values of the wells rate.
        res_param: dictionary
            Reservoir parameters.
        """
        self.controls = well_controls
        self.res_param = res_param
        if res_param['run_folder']:
            self.run_path = os.path.join(res_param['path'],
                                         res_param['run_folder'])
        else:
            self.run_path = os.path.join(res_param['path'])
        if well_controls:
            self.limit_controls = self.limit_variables()
            self.modif_controls = self.multiply_variables()

    def file_to_open(self, name):
        """ Open file."""
        data_folder = Path(self.run_path)
        file = data_folder / name
        return file

    def get_rate_max(self):
        """ Get the maximum rate."""
        nb_prod = self.res_param["nb_prod"]
        prod_max_rate = self.res_param["max_rate_prod"]
        nb_inj = self.res_param["nb_inj"]
        inj_max_rate = self.res_param["max_rate_inj"]
        rates = [prod_max_rate, inj_max_rate]
        repeat = [nb_prod, nb_inj]
        return np.repeat(rates, repeat)

    def cmgfile(self, basename):
        """
        A simple wrapper for retrieving CMG file extensions
        given the basename.
        :param basename:
        :return:
        """
        basename = os.path.join(self.run_path, basename)
        Extension = namedtuple("Extension", "dat out irf mrf rwd \
                               rwo log sr3")
        basename = Extension(basename + ".dat",
                             basename + ".out",
                             basename + ".irf",
                             basename + ".mrf",
                             basename + ".rwd",
                             basename + ".rwo",
                             basename + ".log",
                             basename + ".sr3")
        return basename._asdict()

    def chunks(self):
        """Yield successive n-sized chunks from l."""
        nb_prod = self.res_param["nb_prod"]
        nb_inj = self.res_param["nb_inj"]
        for i in range(0, len(self.controls), (nb_prod + nb_inj)):
            yield self.controls[i: i + nb_prod + nb_inj]

    def limit_variables(self):
        """Create a list of limit value of the variables"""
        time_type = self.res_param["type_time"]
        rate_max = self.get_rate_max()
        nb_cycles = self.res_param["nb_cycles"]
        time_conc = self.res_param["time_concession"]
        if time_type == 1:  # time include as variable
            var = [rate_max, time_conc]
            repeat = [nb_cycles, nb_cycles - 1]
            limit_controls = np.repeat(var, repeat)
        else:
            limit_controls = [rate_max] * nb_cycles
        return limit_controls

    def multiply_variables(self):
        """ Transform the design variables."""
        modif_controls = list()
        for value, limit in zip(self.chunks(), self.limit_variables()):
            modif_controls.append([a * b for a, b in zip(limit, value)])
        return modif_controls

    def time_steps(self):
        """Manipulate the time variable to write in template"""
        # Start cycle - Time ZERO:
        time_type = self.res_param["type_time"]
        nb_cycles = self.res_param["nb_cycles"]
        time_conc = self.res_param["time_concession"]
        time_steps = np.insert(self.modif_controls[-1], 0, 0)

        if time_type == 1:  # time include as design variable
            time_steps = np.cumsum(time_steps)
        else:
            time_steps = np.linspace(start=0, stop=time_conc,
                                     num=nb_cycles + 1)
        return time_steps

    def full_capacity(self):
        """Determine the well ratio of the last well (prod or inj)"""
        max_plat_prod = self.res_param["max_plat_prod"]
        max_plat_inj = self.res_param["max_plat_inj"]
        nb_prod = self.res_param["nb_prod"]
        nb_inj = self.res_param["nb_inj"]
        for index, control in enumerate(self.modif_controls):
            last_prod_well = max_plat_prod - sum(control[:nb_prod])
            last_inj_well = max_plat_inj - sum(control[nb_inj])
            self.modif_controls[index].insert(nb_prod, last_prod_well)
            self.modif_controls[index].append(last_inj_well)
