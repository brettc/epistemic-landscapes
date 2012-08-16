import logging
log = logging.getLogger("simulation")
import agent
import numpy


class SimulationInterrupt(Exception):
    pass


class Simulation(object):
    def __init__(self, treatment, replicate, parameters):
        self.treatment = treatment
        self.replicate = replicate
        self.parameters = parameters

        self.random = numpy.random.RandomState()
        # TODO THINK about how we use seeds
        # self.random.seed(self.parameters.seed)

        self.time_step = 0
        self.agents = []
        self.landscape = self.parameters.landscape
        self.landscape.clear()
        self.make_agents()

    def make_agents(self):
        # log.info("Constructing Agents...")
        self.next_serial = 0
        for cls, num in self.parameters.agents.items():
            self.agents.extend(
                [cls(self, self.next_serial) for i in range(num)])
            self.next_serial += 1

    def agent_types(self):
        return agent.get_agent_class_info()

    def run(self, callbacks=None, progress=None):
        if progress:
            progress.begin(self)

        self.begin()

        for i in range(self.parameters.max_steps):
            self.step()
            if callbacks:
                for c in callbacks:
                    c(self)
            if progress:
                progress.update(self)
                while progress.paused:
                    progress.interact(self)
                if progress.running is False:
                    log.info("User interrupted simulation, ending it ...")
                    raise SimulationInterrupt
            self.time_step += 1

        self.end()

        if progress:
            progress.end(self)

    def begin(self):
        pass

    def step(self):
        self.random.shuffle(self.agents)
        for a in self.agents:
            a.step()

    def end(self):
        pass
