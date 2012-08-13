import logging
log = logging.getLogger("patches")

# import 
import numpy
import operator
import itertools
import os
import cPickle as pickle
import agent

class Patches(object):
    """Contains an array of patches with associated data
    
    This generates the neighbourhoods
    """
    def __init__(self, dims, cache_path=None):

        if cache_path is not None:
            cache_path = os.path.join(cache_path, dims.ident())
            if os.path.exists(cache_path):
                self.load_from_cache(cache_path)
                return

        # These reference the same data, they are just indexed differently
        self.patch_array = numpy.zeros(dims.axes, self.make_dtype(dims))
        self.patch_array_flat = self.patch_array.ravel()

        log.info("Created an array of %d patches", len(self.patch_array_flat))

        # Assign the patches a unique id (their index in the array)
        self.patch_array_flat['index'] = numpy.arange(self.patch_array_flat.size)
        self.generate_indexes(dims)
        self.generate_neighbours(dims)

        if cache_path is not None:
            self.save_to_cache(cache_path)

    def load_from_cache(self, cache_path):
        f = open(cache_path, 'rb')
        self.patch_array = pickle.load(f)
        self.patch_array_flat = self.patch_array.ravel()
        log.info("Loaded patches from cache '%s'", cache_path)

    def save_to_cache(self, cache_path):
        f = open(cache_path, 'wb')
        pickle.dump(self.patch_array, f, -1)
        log.info("Saved patches to cache '%s'", cache_path)

    def generate_indexes(self, dims):
        """Go through every single combination, and generate the values
        """
        ranges = tuple([range(x) for x in dims.axes])

        # We generate every possible combination of parameters here...
        log.info("Generating all patch indexes...")
        for i, values in enumerate(itertools.product(*ranges)):
            self.patch_array_flat['values'][i] = numpy.array(values)

    def generate_neighbours(self, dims):
        log.info("Generating neigbourhoods for %d patches ...",
                 len(self.patch_array_flat))
        # TODO we can get rid of this by using a reshaped array to do the
        # lookup. It should be faster. But it's cached anyway, so let's do it
        # later...
        # # Make a lookup table, so we can find the neighbours
        lookup = dict([(tuple(p['values']), p) for p in self.patch_array_flat])
        # Now generate the neighbours

        for patch_i, p in enumerate(self.patch_array_flat):
            neighbour_i = 0

            # This is slow, so say something ...
            if patch_i != 0 and patch_i % 10000==0:
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

                    # Make the neighbour values (take a copy)
                    # DANGER: numpy uses references by default
                    neighbour_values = values.copy()
                    neighbour_values[i] = v

                    # Look it up
                    otherp = lookup[tuple(neighbour_values)]

                    # TODO ATTEMPTS TO OPTIMIZE
                    # We get a tuple back -- not an array indexable by field
                    # name
                    # test_otherp = self.patch_array_x.item(*neighbour_values)
                    # print self.patch_array_x.shape
                    # print neighbour_values
                    # print test_otherp
                    # print otherp
                    # assert otherp['index'] == test_otherp['index']

                    other_i = otherp['index']
                    p['neighbours'][neighbour_i] = other_i

                    # Go to the next neighbour
                    neighbour_i += 1


    def make_dtype(self, dims):
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
            ('values', numpy.int32, dims.dimensionality()),
            ('neighbours', numpy.int32, dims.neighbourhood_size()),

            # This allows us to cache data in a python object during the
            # search
            ('cache', object),
            ])

    clear_list = 'visits', 'visits_by_type'
    def clear(self):
        for c in self.clear_list:
            self.patch_array_flat[c] = 0
