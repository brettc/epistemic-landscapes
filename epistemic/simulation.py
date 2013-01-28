import logging
log = logging.getLogger("simulation")

import numpy
import pytreatments
import agent
import placement


class Simulation(pytreatments.Simulation):

    def on_begin(self):
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
        self.default_placement = placement.random_placement()
        self.default_placement.sim = self
        self.placements = set([self.default_placement])

        for cls, num, pc in self.parameters.agents_to_create:
            new_agents = [cls(self) for i in range(num)]
            if pc is None:
                pc = self.default_placement
            elif pc not in self.placements:
                pc.sim = self
                self.placements.add(pc)

            # Add to simulation and to the placement algorithm
            self.agents.extend(new_agents)
            pc.agents.extend(new_agents)

        for p in self.placements:
            p.place()


    def on_step(self):
        log.info("Stepping ...")
        self.random.shuffle(self.agents)
        for a in self.agents:
            a.step()
        return True

    def on_end(self):
        pass

    def agent_types(self):
        return agent.get_agent_class_info()
