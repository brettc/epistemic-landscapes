import logging
log = logging.getLogger("parameters")

import copy
import pytreatments

class ParametersError(Exception):
    pass

class Parameters(pytreatments.Parameters):
    # Put the default parameters here
    seed = 0
    landscape = None
    max_steps = 100
    # Followers move this often, even when the move is not better
    follower_move_p = .01

    # Anything above this is the good stuff
    significance_cutoff = .5

    def __init__(self, **kwargs):
        self.agents = {}
        for k, v in kwargs.items():
            if hasattr(self, k):
                log.info("Setting '%s' to %s", k, v)
                setattr(self, k, v)
            else:
                log.warning("'%s' is not a valid parameter (ignoring)", k)

    def set_agents(self, kind, number):
        self.agents[kind] = number

    def freeze(self):
        # Need to go a bit deeper with agents
        c = copy.copy(self)
        c.agents = self.agents.copy()
        return c

