import logging

log = logging.getLogger("simulation")

import numpy
import agent
import placement
import patch_control

class Interrupt(Exception):
    pass


class BaseProgress(object):
    def __init__(self):
        self.running = True
        self.paused = False

    def begin(self, sim):
        pass

    def update(self, sim):
        pass

    def interact(self, sim):
        pass

    def end(self, sim):
        pass


class Simulation(object):
    def __init__(self, seed, treatment_name, replicate_seq, parameters):
        self.seed = seed
        self.treatment_name = treatment_name
        self.replicate_seq = replicate_seq
        self.description = "T{0.treatment_name} R{0.replicate_seq:0>3}".format(self)
        self.time_step = 0
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

    def run(self, history=None, callbacks=None, progress=None):
        if progress:
            progress.begin(self)

        while 1:
            self.more = self.step(history)

            if callbacks:
                for c in callbacks:
                    c(self)
            if progress:
                progress.update(self)
                while progress.paused:
                    progress.interact(self)
                if progress.running is False:
                    log.info("User interrupted simulation...")
                    self.more = False

            if not self.more:
                break

            # Update time step after we've done all the processing
            self.time_step += 1

        if progress:
            progress.end(self)

    def step(self, history):
        log.info("Stepping ...")
        self.random.shuffle(self.agents)
        for a in self.agents:
            a.step()

        if self.time_step + 1 == self.parameters.max_steps:
            return False

        return True

    def agent_types(self):
        return agent.get_agent_class_info()
