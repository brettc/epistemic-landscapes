import logging
log = logging.getLogger("analysis.trace")

from base import ReplicateAnalysis, register_analysis

class TraceAgent(object):
    def __init__(self, a):
        # Eek. Referencing loop...
        self.agent = a
        a._trace = self

        self.stuck = 0
        self.new = None
        self.old = 1
        self.update()

    def update(self):
        if self.old == self.new:
            self.stuck += 1
        self.old = self.new
        self.new = self.agent.patch['index']
        self.report()

    def report(self):
        # TODO Lot more could be said here. Also, we could output it to a
        # separate file rather than log it.

        log.info('%s %d moves from %s to %s: patches seen=%s, stuck=%s', 
                 self.agent.typename,
                 self.agent.serial, 
                 self.old,
                 self.new,
                 len(self.agent.visited),
                 self.stuck
                )

@register_analysis
class trace(ReplicateAnalysis):
    def begin_replicate(self, sim):
        self.tracers = [TraceAgent(a) for a in sim.agents]

    def step(self, sim):
        # Do it this way to preserve order. The agents will have moved in
        # their current sorted order
        log.info('----------- Step number %s --------------' % sim.time_step)
        for a in sim.agents:
            a._trace.update()

    def end_replicate(self, sim):
        # Get rid of recursive data structures
        self.tracers = []

