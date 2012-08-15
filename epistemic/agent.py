import logging
log = logging.getLogger("")

#------------------------------------------------------------------------ 
# Class factory information
agent_types = 0
agent_classes = []

def add_to_factory(agent):
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

    def __init__(self, sim, serial):
        self.sim = sim
        self.serial = serial

        self.best = 0.0
        self.patch = None

        self.visited = set()
        self.place_randomly()

    def __repr__(self):
        return "<Agent: %s>" % (self.serial)

    @property
    def typename(self):
        return self.__class__.__name__

    def move(self, p):
        if p is self.patch:
            # We're already there...
            return

        # Update Patch stats
        p['visits'] += 1
        p['visits_by_type'][self.typeid] += 1

        # Update the agent
        self.patch = p

        # Cache some useful local neighbourhood info about the patch
        if p['cache'] == 0:
            n = [self.sim.landscape[i] for i in self.patch['neighbours']]
            p['cache'] = n

        # Assign the current neighbours to agent
        self.neighbours = p['cache']

        # Update Agent stats
        self.visited.add(p['index'])
        f = self.patch['fitness']
        if f > self.best:
            self.best = f

    def place_randomly(self):
        choice = self.sim.random.randint(0, len(self.sim.landscape))
        p = self.sim.landscape[choice]
        self.move(p)

    def randomly_choose(self, choices):
        if choices:
            l = len(choices)
            if l == 1:
                return choices[0]
            i = self.sim.random.randint(0, l)
            return choices[i]

    def nominate_random(self):
        return self.randomly_choose(self.neighbours)

    def nominate_unvisited(self):
        unvisited = [p for p in self.neighbours if p['visits'] == 0]
        return self.randomly_choose(unvisited)

    def nominate_random_visited(self):
        visited = [p for p in self.neighbours if p['visits'] > 0]
        return self.randomly_choose(visited)

    def nominate_best_visited(self):
        visited = [p for p in self.neighbours if p['visits'] > 0]
        if not visited:
            return None
        if len(visited) == 1:
            return visited[0]
        visited.sort(key=lambda p: p['fitness'])
        # TODO Pick randomly among BEST if there ties 
        return visited[-1]

#------------------------------------------------------------------------ 
# Actual classes defined here

@add_to_factory
class Drunk(Agent):
    """The Drunk does a random walk"""
    def step(self):
        p = self.nominate_random()
        self.move(p)

@add_to_factory
class Maverick(Agent):
    """A Maverick prefers unvisited cells, otherwise it chooses the best. If
    none are better it stays put.
    """
    def step(self):
        p = self.nominate_unvisited()
        if p is None:
            # Everything has been visited, so now find the best.
            p = self.nominate_best_visited()
            # if p['fitness'] < self.patch['fitness']:
                # return 
        self.move(p)

@add_to_factory
class Follower(Agent):
    """The Follower chooses the best in the neighbourhood. If they're all
    worse then they simply stop. They do have a small experimentation rate.
    """
    def step(self):
        p = self.nominate_best_visited()
        if p is None:
            # Everything has been visited; pick one at random.
            p = self.nominate_random()
        elif p['fitness'] < self.patch['fitness']:
            # We're in the best spot
            # Very seldom, we'll move somewhere even though it's worse
            move_anyway = self.sim.random.uniform(0.0, 1.0)
            if move_anyway > self.sim.parameters.follower_move_p:
                # Stay put 
                return
            # Hm, maybe should select on basic of difference from current fit?
            p = self.nominate_random()

        self.move(p)


