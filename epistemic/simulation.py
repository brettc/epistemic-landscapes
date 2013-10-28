import logging

log = logging.getLogger("simulation")

import numpy
import pytreatments
import agent
import placement
import patch_control


class Simulation(pytreatments.Simulation):
    def __init__(self, seed, treatment_name, replicate_seq, parameters):
        pytreatments.Simulation.__init__(
            self, seed, treatment_name, replicate_seq)
        self.parameters = parameters
        log.info("Randomizing...")
        self.random = numpy.random.RandomState()
        self.random.seed(self.parameters.seed)
        self.landscape = self.parameters.landscape
        self.patch_controller = patch_control.PatchController(
            patches=self.landscape.patches,
            depth=self.parameters.neighbourhood_size,
            random_state=self.random
        )
        self.agents = []
        self.next_serial = 0
        self.default_placement = placement.random_placement()
        self.default_placement.sim = self
        self.placements = {self.default_placement}

    @property
    def begin(self):
        log.info("Clearing Landscape...")
        # Note that this is necessary because we SHARE landscape data
        # TODO: This should pbly be fixed, so that we have STATIC and DYNAMIC
        # arrays...

        self.landscape.clear()

        log.info("Constructing Agents...")
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

        return True

    def step(self, history):
        log.info("Stepping ...")
        self.random.shuffle(self.agents)
        for a in self.agents:
            a.step()

        if self.time_step + 1 == self.parameters.max_steps:
            return False

        return True

    def on_end(self):
        pass

    def agent_types(self):
        return agent.get_agent_class_info()
