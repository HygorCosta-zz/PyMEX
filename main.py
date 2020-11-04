""" Run PyMex.
# -*- coding: utf8 -*-
# Copyright (c) 2019 Hygor Costa
#
# This file is part of Py_IMEX.
#
# You should have received a copy of the GNU General Public License
# along with HUM.  If not, see <http://www.gnu.org/licenses/>.
#
# Created: Sept 2019
# Author: Hygor Costa
"""
import yaml
# from utilits import PyMEX
# from utilits import PlotImex
from utilits import ParallelPyMex

if __name__ == "__main__":
    # Create the hypothetical controls
    controls1 = [0.5, 0.5, 1]*2
    controls2 = [0.7, 0.3, 0.8]*2
    controls = [controls1, controls2]

    with open('./reservoir_config.yaml') as f:
        res_param = yaml.load(f, Loader=yaml.FullLoader)

    model = ParallelPyMex(controls, res_param, pool_size=None)
    npv = model.pool_pymex()
    print(npv)

    # Run just with PyMEX.
    # model_plots = PlotImex(model.report_resul)
    # model_plots.plot_cumulative_production()
