import logging
import numpy
import agent

log = logging.getLogger("stats")


def _count_true(x):
    # Count the number of True values
    return float(sum(x))


class AgentStats(object):
    """Use to store stats per Agent type"""
    def __init__(self, st, i):
        assert isinstance(st, Stats)
        self.st = st
        self.agent_type = i
        self._calculate()

    def _calculate(self):
        _p = self.st.patches
        v = _p['visits_by_type'][:, self.agent_type]
        self.visited = v > 0
        self.visit_count = _count_true(self.visited)

        self.nz_visited = numpy.logical_and(self.visited, self.st.nonzero)
        self.nz_visited_count = _count_true(self.nz_visited)

        self.coverage = self.visit_count / self.st.patch_count
        self.progress = self.nz_visited_count / self.st.nz_count
        self.knowledge = sum(_p[self.visited]['fitness'])


class Stats(object):
    def __init__(self, patches):
        self.patches = patches
        self._calculate()
        self.per_agent = [AgentStats(self, i) for i in range(agent.agent_types)]

    def _calculate(self):
        # To ease readability
        _p = self.patches

        self.patch_count = float(_p.size)

        self.visited = _p['visits'] > 0
        self.nonzero = _p['fitness'] > 0.0
        self.nz_visited = numpy.logical_and(self.visited, self.nonzero)

        self.nz_count = _count_true(self.nonzero)
        self.visited_count = _count_true(self.visited)
        self.nz_visited_count = _count_true(self.nz_visited)

        self.coverage = self.visited_count / self.patch_count
        self.progress = self.nz_visited_count / self.nz_count
        self.knowledge = sum(_p[self.visited]['fitness'])


