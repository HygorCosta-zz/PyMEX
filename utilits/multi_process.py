""" Parallel computation. """
import multiprocessing as mp
import numpy as np
from .ManiParam import PyMEX


class ParallelPyMex:

    """Run imex in parallel for reservoir optimization."""

    def __init__(self, controls, template, res_param, pool_size=None):
        """TODO: to be defined.

        Parameters
        ----------
        controls: array
            Solution candidates for design variables.
        res_param: dictionary
            Reservoir parameters
        pool_size: int
            Pool size for multiprocessing, if pool_size is None
            so it's sequential.

        """
        self.controls = controls
        self.tpl = template
        self.res_param = res_param
        self.pool_size = pool_size

    def run_sequential(self):
        """ Run PyMEX in a sequential way."""
        npv = []
        if self.controls.ndim == 1:
            model = PyMEX(self.controls, self.tpl, self.res_param)
            model.call_pymex()
            npv = model.npv
        else:
            for control in self.controls:
                model = PyMEX(control, self.tpl, self.res_param)
                model.call_pymex()
                npv = np.append(npv, model.npv)
        return npv

    def run_parallel(self, control):
        """ Run PyMEX with Pool."""
        model = PyMEX(control, self.tpl, self.res_param)
        model.call_pymex()
        return model.npv

    def pool_pymex(self):
        """ Run imex in parallel.

        Parameters
        ----------
        pool_size: int
            Number of process.

        """
        if self.pool_size is not None and self.controls.ndim != 1:
            with mp.Pool(self.pool_size) as proc:
                npv = proc.map(self.run_parallel, self.controls)
        else:
            npv = self.run_sequential()
        return np.array(npv)
