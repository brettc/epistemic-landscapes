import logging
log = logging.getLogger("patches")

# import
import numpy
import itertools
import os
import cPickle as pickle
import agent
import dimensions
from pytreatments import active


class Patches(object):
    """Contains an array of patches with associated data

    This generates the neighbourhoods
    """
    def __init__(self, dims, cache_path=None):

        self.dims = dims

        if cache_path is not None:
            cache_path = os.path.join(cache_path, dims.ident())
            if os.path.exists(cache_path):
                self.load_from_cache(cache_path)
                return

        # These reference the same data, they are just indexed differently
        self.patch_array = numpy.zeros(
            self.dims.axes,
            self.make_dtype())
        self.patch_array_flat = self.patch_array.ravel()

        log.info("Created an array of %d patches", len(self.patch_array_flat))

        # Assign the patches a unique id (their index in the array)
        self.patch_array_flat['index'] = numpy.arange(
            self.patch_array_flat.size)
        self.generate_indexes()
        self.generate_neighbours()

        if cache_path is not None:
            self.save_to_cache(cache_path)

    @property
    def size(self):
        return len(self.patch_array_flat)

    def __len__(self):
        return self.size

    def __iter__(self):
        for i in range(self.size):
            yield self[i]

    def __getitem__(self, i):
        if self.patch_array_flat['cache'][i] == 0:
            p = Patch(self, i)
            self.patch_array_flat['cache'][i] = p
            return p

        return self.patch_array_flat['cache'][i]

    def load_from_cache(self, cache_path):
        f = open(cache_path, 'rb')
        self.patch_array = pickle.load(f)
        self.patch_array_flat = self.patch_array.ravel()
        log.info("Loaded patches from cache '%s'", cache_path)

    def save_to_cache(self, cache_path):
        f = open(cache_path, 'wb')
        pickle.dump(self.patch_array, f, -1)
        log.info("Saved patches to cache '%s'", cache_path)

    def generate_indexes(self):
        """Go through every single combination, and generate the values
        """
        dims = self.dims
        ranges = tuple([range(x) for x in dims.axes])

        # We generate every possible combination of parameters here...
        log.info("Generating all patch indexes...")
        for i, values in enumerate(itertools.product(*ranges)):
            self.patch_array_flat['values'][i] = numpy.array(values)

    def generate_neighbours_slow(self):
        log.info("Generating neigbourhoods for %d patches ...",
                 len(self.patch_array_flat))

        dims = self.dims

        # # Make a lookup table, so we can find the neighbours
        lookup = dict([(tuple(p['values']), p) for p in self.patch_array_flat])
        # Now generate the neighbours

        for patch_i, p in enumerate(self.patch_array_flat):
            neighbour_i = 0

            # This is slow, so say something ...
            if patch_i != 0 and patch_i % 1000 == 0:
                log.info("     Working ... (%d Patches complete)", patch_i)

            # Get the axis values that identify this patches
            values = p['values']
            # Go along each axis, and generate the alternatives
            for i, a in enumerate(dims.axes):
                curval = values[i]
                for v in range(a):
                    # Ignore it if it is the same
                    if v == curval:
                        continue

                    # Make the neighbour values (take a copy) DANGER: numpy
                    # uses references by default
                    neighbour_values = values.copy()
                    neighbour_values[i] = v

                    # Look it up
                    otherp = lookup[tuple(neighbour_values)]

                    other_i = otherp['index']
                    p['neighbours'][neighbour_i] = other_i

                    # Go to the next neighbour
                    neighbour_i += 1

    def generate_neighbours_fast(self):
        log.info("Generating neigbourhoods for %d patches ...",
                 len(self.patch_array_flat))

        dims = self.dims
        for patch_i, p in enumerate(self.patch_array_flat):
            neighbour_i = 0

            # This is slow, so say something ...
            if patch_i != 0 and patch_i % 1000 == 0:
                log.info("     Working ... (%d Patches complete)", patch_i)

            # Get the axis values that identify this patches
            values = p['values']
            # Go along each axis, and generate the alternatives
            axes = numpy.array(dims.axes)
            for i, a in enumerate(dims.axes):
                curval = values[i]
                neighbour_values = values.copy()
                for v in range(a):
                    # Ignore it if it is the same
                    if v == curval:
                        continue

                    neighbour_values[i] = v

                    # index is just the product of the axes
                    idx = sum(neighbour_values * axes)
                    p['neighbours'][neighbour_i] = idx

                    # Go to the next neighbour
                    neighbour_i += 1

    def make_dtype(self):
        """Return a data type for constructing a numpy array

        This allows us to keep all the data in one big array.
        It also means that any use of cython can get access to raw "C" values
        for fast manipulation.
        """

        # TODO Move this data structure out somewhere else?
        #
        return numpy.dtype([
            # Unique id for each patch
            ('index', numpy.int32),

            # Data need for each patch
            # add more stuff here...
            ('visits', numpy.int32),
            ('visits_by_type', numpy.int32, agent.agent_types),

            ('fitness', numpy.float64),

            # Lookups, so we can easily find neighbours.
            # We generate this stuff above
            ('values', numpy.int32, self.dims.dimensionality()),
            ('neighbours', numpy.int32, self.dims.neighbourhood_size()),

            # This allows us to cache data in a python object during the
            # search
            ('cache', object),
        ])

    clear_list = 'visits', 'visits_by_type', 'cache'

    def clear(self):
        for c in self.clear_list:
            self.patch_array_flat[c] = 0

    # The fast one is currently slower and wrong!
    generate_neighbours = generate_neighbours_slow


class Patch(object):
    """This just provides simplified Object-Like access to the patch array"""

    def __init__(self, patches, index):
        self._patches = patches
        self._p = patches.patch_array_flat[index]
        self._n = None

    def __repr__(self):
        return "<Patch:{0.index:}|F:{0.fitness:0>4.4}>".format(self)

    @property
    def neighbours(self):
        if self._n is not None:
            return self._n

        # Okay, let's work it out
        self._n = [self._patches[i] for i in self._neighbours]
        return self._n

    def visit(self, a):
        self.visits += 1
        self.visits_by_type[a.typeid] += 1

        # TODO: We could do some clever updating of other patches here
        #
    def randomly_choose(self, choices):
        if choices:
            l = len(choices)
            if l == 1:
                return choices[0]
            i = active.sim.random.randint(0, l)
            return choices[i]

        return None

    def random_neighbour(self):
        return self.randomly_choose(self.neighbours)

    def unvisited_neighbour(self):
        unvisited = [p for p in self.neighbours if p.visits == 0]
        return self.randomly_choose(unvisited)

    def visited_neighbour(self):
        visited = [p for p in self.neighbours if p.visits > 0]
        return self.randomly_choose(visited)

    def best_neighbour(self):
        visited = [p for p in self.neighbours if p.visits > 0]
        if not visited:
            return None
        if len(visited) == 1:
            return visited[0]

        # Find the best (equal)
        # Start with impossible negative score
        best_score = -1.0
        for v in visited:
            f = v.fitness
            if f > best_score:
                best = [v]
                best_score = f
            elif f == best_score:
                best.append(v)

        return self.randomly_choose(best)


# We magically add some extra "simple" properties. This is just short-hand,
# rather than manually adding a bunch of properties one at a time. It's also
# easier to extend
def make_patch_property(pname):
    if pname.startswith('_'):
        fieldname = pname[1:]
    else:
        fieldname = pname

    def getter(self):
        return self._p[fieldname]

    def setter(self, x):
        self._p[fieldname] = x

    # Now add these functions into the class
    setattr(Patch, pname, property(getter, setter))

simple_props = ('index', 'visits', 'visits_by_type', 'fitness', '_values',
                '_neighbours')

# This is the list of automatic properties
for pname in simple_props:
    make_patch_property(pname)


def make_patches():
    d = dimensions.Dimensions()
    d.add_dimensions(2, 4)
    ps = Patches(d)
    p = ps[0]
    print p
    print p.visits
    p.visits = 10
    p.fitness = 3.5
    ps[5].fitness = 5.0
    print ps.patch_array_flat
    print ps[5].neighbours

if __name__ == "__main__":
    make_patches()
    # from timeit import Timer
    # t = Timer("make_patches()", "from __main__ import make_patches")
    # print t.timeit(number=1)
    # Patches.generate_neighbours = Patches.generate_neighbours_fast
    # t = Timer("make_patches()", "from __main__ import make_patches")
    # print t.timeit(number=1)
