import numpy


class PatchController(object):
    def __init__(self, patches, depth=1, random_state=numpy.random):
        """
        @param patches: The patches!
        @param depth: How deep the neighbourhood goes
        @param random_state: Supplier of random numbers
        """
        self.patches = patches
        self.depth = depth
        self.random_state = random_state
        self.array = self.patches.patch_array_flat

    @property
    def size(self):
        return len(self.array)

    def __len__(self):
        return self.size

    def __iter__(self):
        for i in range(self.size):
            yield self[i]

    def __getitem__(self, i):
        """We return the Patch class proxy for the row in the array"""
        if self.array['cache'][i] == 0:
            p = Patch(self, i)
            self.array['cache'][i] = p
            return p

        return self.array['cache'][i]


class Patch(object):
    """This just provides simplified Object-Like access to the patch array"""
    __slots__ = {'_pc', '_p', '_n'}

    def __init__(self, pc, index):
        """
        @type pc: PatchController
        @param index: Where in the array is it?
        """
        self._pc = pc
        self._p = pc.array[index]
        self._n = None

    def __repr__(self):
        return "<P:{1:}|F:{0.fitness:0>4.4}>".format(
            self, "".join([str(v) for v in self.values]))

    @property
    def neighbours(self):
        """This lazily accesses the underlying _neighbours variable,
        but extends it to make it pythonic, and multi-level
        """
        if self._n is not None:
            return self._n


        full_set = set()
        curr_set = {self}
        next_set = set()

        depth = self._pc.depth

        while depth > 0:
            for p in curr_set:
                next_set.update([self._pc[i] for i in p._neighbours])
            full_set |= next_set
            curr_set = next_set
            next_set = set()
            depth -= 1

        # TODO: Do we really need a list here? Or is a set better?
        self._n = list(full_set)
        return self._n

    # TODO: We could do some clever updating of other patches here
    def visit(self, a):
        self.visits += 1
        self.visits_by_type[a.typeid] += 1

    def randomly_choose(self, choices):
        if not choices:
            return None
        l = len(choices)
        if l == 1:
            return choices[0]
        i = self._pc.random_state.randint(0, l)
        return choices[i]

    def random_neighbour(self):
        return self.randomly_choose(self.neighbours)

    def unvisited_neighbour(self):
        unvisited = [p for p in self.neighbours if p.visits == 0]
        return self.randomly_choose(unvisited)

    def visited_neighbour(self):
        visited = [p for p in self.neighbours if p.visits > 0]
        return self.randomly_choose(visited)

    @property
    def best_neighbour(self):
        visited = [p for p in self.neighbours if p.visits > 0]
        if not visited:
            return None
        if len(visited) == 1:
            return visited[0]

        # Find the best (equal)
        # Start with impossible negative score
        best_score = -1.0
        best = None
        for v in visited:
            f = v.fitness
            if f > best_score:
                best = [v]
                best_score = f
            elif f == best_score:
                best.append(v)

        assert best is not None
        return self.randomly_choose(best)


# We magically add some extra "simple" properties. This is just short-hand,
# rather than manually adding a bunch of properties exactly the same way. It's
# also easier to extend
def make_patch_property(pname):
    if pname.startswith('_'):
        field_name = pname[1:]
    else:
        field_name = pname

    def getter(self):
        return self._p[field_name]

    def setter(self, x):
        self._p[field_name] = x

    # Now add these functions into the class
    setattr(Patch, pname, property(getter, setter))

# This is the list of automatic properties. Names beginning in underscore get
# it removed, and reference the name without it. These are fields defined in
# the dtype of the numpy array (see above)
simple_props = ('index', 'visits', 'visits_by_type', 'fitness', 'values',
                '_neighbours')

# Add all the automatic properties to the class
for property_name in simple_props:
    make_patch_property(property_name)

