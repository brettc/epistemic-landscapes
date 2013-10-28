import logging

log = logging.getLogger("patches")

# import
import numpy
import itertools
import os
import cPickle as pickle
import agent


class Patches(object):
    """Contains an array of patches with associated data

    This generates the neighbourhoods
    """

    def __init__(self, dims, depth=1, cache_path=None):

        self.dims = dims
        self.depth = depth

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

    def __getitem__(self, i):
        return self.patch_array_flat[i]

    @property
    def size(self):
        return len(self.patch_array_flat)

    def __len__(self):
        return self.size

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
        log.info("Generating neighbourhoods for %d patches ...",
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
        # TODO: Note that this is currently fucked
        log.info("Generating neighbourhoods for %d patches ...",
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

        # TODO: Move this data structure out somewhere else?
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

    # TODO: The fast one is currently slower and wrong!
    generate_neighbours = generate_neighbours_slow


