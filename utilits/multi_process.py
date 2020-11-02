""" Parallel computation. """
import multiprocessing as mp
# from pathos.multiprocessing import ProcessingPool as Pool
from utilits import PyMEX


class ParallelPyMex:

    """Run imex in parallel for reservoir optimization."""

    def __init__(self, controls, res_param, pool_size=None):
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
        self.res_param = res_param
        self.pool_size = pool_size

    def run_sequential(self):
        """ Run PyMEX in a sequential way."""
        npv = []
        for control in self.controls:
            model = PyMEX(control, self.res_param)
            model.call_pymex()
            npv.append(model.net_present_value)
        return npv

    def run_parallel(self, control):
        """ Run PyMEX with Pool."""
        model = PyMEX(control, self.res_param)
        # model.call_pymex()
        # return model.net_present_value
        return model.basename

    def pool_pymex(self):
        """ Run imex in parallel.

        Parameters
        ----------
        pool_size: int
            Number of process.

        """
        if self.pool_size is not None:
            with mp.Pool(self.pool_size) as proc:
                npv = proc.map(self.run_parallel, self.controls)
        else:
            npv = self.run_sequential()
        return npv
