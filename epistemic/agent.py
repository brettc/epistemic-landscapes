import logging
log = logging.getLogger("")

#------------------------------------------------------------------------
# Class factory information
agent_types = 0
agent_classes = []


def register_agent(agent):
    global agent_classes
    global agent_types
    agent_classes.append(agent)

    # Stick in a type id for referencing them. This will be useful for
    # referencing arrays and the like.
    agent.typeid = agent_types
    agent_types += 1

    return agent


def get_agent_class_info():
    global agent_classes
    return [(a.__name__, a.typeid) for a in agent_classes]


def get_agent_class_names():
    global agent_classes
    names = [a.__name__ for a in agent_classes]
    return names


class Agent(object):

    def __init__(self, sim):
        self.sim = sim
        self.serial = sim.next_serial
        sim.next_serial += 1

        self.best = 0.0
        self.location = None

        self.visited = set()

    def __repr__(self):
        return "<%s: %s>" % (self.typename(), self.serial)

    @property
    def typename(self):
        return self.__class__.__name__

    def move(self, p):
        if p is self.location:
            # We're already there...
            return

        p.visit(self)

        # Update Agent stats
        self.visited.add(p)
        f = p.fitness
        if f > self.best:
            self.best = f

        # Update the agent
        self.location = p



#------------------------------------------------------------------------
# Actual classes defined here


@register_agent
class Drunk(Agent):
    """The Drunk does a random walk"""
    def step(self):
        p = self.location.random_neighbour()
        self.move(p)


@register_agent
class Maverick(Agent):
    """A Maverick prefers unvisited cells, otherwise it chooses the best. If
    none are better it stays put.
    """
    def step(self):
        p = self.location.unvisited_neighbour()
        if p is None:
            # Everything has been visited, so now find the best.
            p = self.location.best_neighbour()
            # if p['fitness'] < self.location['fitness']:
                # return
        self.move(p)


@register_agent
class Follower(Agent):
    """The Follower chooses the best in the neighbourhood. If they're all
    worse then they simply stop. They do have a small experimentation rate.
    """
    def step(self):
        p = self.location.best_neighbour()
        if p is None:
            # Everything has been visited; pick one at random.
            p = self.location.random_neighbour()
        elif p.fitness < self.location.fitness:
            # We're in the best spot
            # Very seldom, we'll move somewhere even though it's worse
            move_anyway = self.sim.random.uniform(0.0, 1.0)
            if move_anyway > self.sim.parameters.follower_move_p:
                # Stay put
                return
            # Hm, maybe should select on basic of difference from current fit?
            p = self.location.random_neighbour()

        self.move(p)
