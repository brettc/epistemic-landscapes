import logging
log = logging.getLogger("placement")

placement_classes = set()


def register_placement(p):
    global placement_classes
    placement_classes.add(p)
    return p


class Placement(object):
    """Base class for different placement algorithms"""
    def __init__(self):
        self.sim = None
        self.agents = []

    def place(self):
        raise NotImplementedError

    def find_low_significance(self):
        pass


@register_placement
class random_placement(Placement):
    def place(self):
        log.info("Placing %d agents randomly", len(self.agents))
        for a in self.agents:
            choice = self.sim.random.randint(0, len(self.sim.patch_controller))
            p = self.sim.patch_controller[choice]
            a.move(p)


@register_placement
class point_placement(Placement):
    # TODO: Fix this

    def place(self):
        log.info("Placing %d agents at a point p", len(self.agents))
        for a in self.agents:
            p = self.sim.patch_controller[0]
            a.move(p)


# class cloud_placement(Placement):
    # def place(self):

        # pass
