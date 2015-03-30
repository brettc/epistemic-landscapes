import logging
log = logging.getLogger("analysis.trace")

from .. import plugin

class TraceAgent(object):
    def __init__(self, a, output):
        # Eek. Referencing loop...
        self.agent = a
        a._trace = self

        self.stuck = 0
        self.old = None
        self.new = a.location
        self.update(output)

    def update(self, output):
        if self.old == self.new:
            self.stuck += 1
        self.old = self.new
        self.new = self.agent.location
        self.report(output)

    def report(self, output):
        # TODO Lot more could be said here. Also, we could output it to a
        # separate file rather than log it.

        text = '%s %d moves from %s(%f) to %s(%f): patches seen=%s, stuck=%s' % (
            self.agent.typename,
            self.agent.serial,
            self.old.index if self.old else -1,
            self.old.fitness if self.old else 0.0,
            self.new.index if self.new else -1,
            self.new.fitness if self.old else 0.0,
            len(self.agent.visited),
            self.stuck
        )
        output.write(text)
        output.write('\n')

        # log.info('%s %d moves from %s to %s: patches seen=%s, stuck=%s',
                 # self.agent.typename,
                 # self.agent.serial,
                 # self.old,
                 # self.new,
                 # len(self.agent.visited),
                 # self.stuck
                # )

@plugin.register_plugin
class trace(plugin.Plugin):
    def begin_simulation(self, sim):
        self.output = self.get_file('trace.txt')
        self.tracers = [TraceAgent(a, self.output) for a in sim.agents]

    def step(self, sim):
        # Do it this way to preserve order. The agents will have moved in
        # their current sorted order
        # log.info('----------- Step number %s --------------' % sim.time_step)
        for a in sim.agents:
            a._trace.update(self.output)


