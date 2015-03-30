import logging
log = logging.getLogger("history")
import os
import time


class History(object):
    def __init__(self, pth, sim=None, replicate_seed=None):
        self.path = pth

        if sim is not None:
            self.running = True
            self.mode = 'w'
            self.init(sim)
        else:
            assert replicate_seed is not None
            self.mode = 'r'
            self.mark_time()
            sim = self.load()
            log.debug("Loading history from %s took %f seconds",
                      pth, self.report_time())
            self.running = False

            # Verify that the seed is the same (ensures stability of analysis
            # under changing code)
            if sim.seed != replicate_seed:
                log.warning(
                    "The replicate seed (%d) given by the experiment is different "
                    "from the saved seed (%d) in the history!",
                    replicate_seed, self.sim.seed)

            # Extra verification can be built into here
            self.verify()

    def mark_time(self):
        self.start_counting = time.clock()

    def report_time(self):
        return time.clock() - self.start_counting

    def load(self):
        pass

    def init(self, sim):
        pass

    def close(self):
        pass

    def verify(self):
        pass
