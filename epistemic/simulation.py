import logging
log = logging.getLogger("simulation")

import pytreatments

import agent
import numpy


class Simulation(pytreatments.Simulation):

    def begin(self):
        log.info("Randomizing...")
        self.random = numpy.random.RandomState()
        self.random.seed(self.parameters.seed)

        log.info("Clearing Landscape...")
        self.landscape = self.parameters.landscape
        self.landscape.clear()

        # Make the agents
        log.info("Constructing Agents...")
        self.next_serial = 0
        self.agents = []
        for cls, num in self.parameters.agents.items():
            self.agents.extend([cls(self) for i in range(num)])

    def step(self):
        log.info("Stepping ...")
        self.random.shuffle(self.agents)
        for a in self.agents:
            a.step()
        return True

    def end(self):
        pass

    def agent_types(self):
        return agent.get_agent_class_info()
