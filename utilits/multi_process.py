""" Parallel computation. """
import multiprocessing as mp
import numpy as np


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

    def __call__(self):
        """ Run PyMEX in a sequential way."""
        if self.controls.ndim == 1:
            model = PyMEX(self.controls, self.tpl, self.res_param)
            model.call_pymex()
        else:
            for control in self.controls:
                model = PyMEX(control, self.tpl, self.res_param)
                model.call_pymex()
        return model
