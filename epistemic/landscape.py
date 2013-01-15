import logging
log = logging.getLogger("landscape")

# import
import numpy
from numpy import random as numpy_random
import operator
import itertools
import os
import cPickle as pickle
import agent


class Dimensions(object):
    """Represents the dimensions of the space"""
    def __init__(self, dim_tuples=[]):
        self.axes = []
        self.axes_by_size = {}

        # What if we're given just a single tuple?
        if len(dim_tuples) == 2:
            sz, hm = tuple(dim_tuples)
            if isinstance(sz, type(1)) and isinstance(hm, type(1)):
                self.add_dimensions(sz, hm)
                return

        for sz, hm in dim_tuples:
            self.add_dimensions(sz, hm)

    def add_dimensions(self, size, how_many):
        self.axes.extend([size] * how_many)
        try:
            n = self.axes_by_size[size]
        except KeyError:
            n = 0
        n += how_many
        self.axes_by_size[size] = n

    def dimensionality(self):
        return len(self.axes)

    def ident(self):
        # Unique ident for axes -- use for caching landscapes
        return self.dim_str() + '.patches'

    def neighbourhood_size(self):
        # Calculate possible one-step neighbours
        # Each dimension can vary by 1 less than it's size
        return reduce(operator.add, [x - 1 for x in self.axes])

    def size(self):
        return reduce(operator.mul, self.axes)

    def dim_str(self):
        ax = sorted(self.axes_by_size.items())
        return '-'.join(['%sx%s' % (k, v) for k, v in ax])


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
        self.patch_array_flat['index'] = numpy.arange(
            self.patch_array_flat.size)
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
            if patch_i != 0 and patch_i % 10000 == 0:
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


# See here:
# http://numpy-discussion.10968.n7.nabble.com/Generating-random-samples-without-repeats-td25666.html
def sample_without_repeats(M, N):
    return numpy.random.rand(M).argsort()[:N]


class Landscape(object):
    """Maybe we'll manually define one later, so keep a base class"""
    def __init__(self, dims, cache_path=None):
        self.dims = dims
        self.patches = Patches(dims, cache_path)

    def clear(self):
        self.patches.clear()

    @property
    def data(self):
        return self.patches.patch_array_flat

    # Emulate a readonly container
    def __getitem__(self, i):
        return self.patches.patch_array_flat[i]

    def __len__(self):
        return len(self.patches.patch_array_flat)

    def __iter__(self):
        return iter(self.patches.patch_array_flat)


class NKLandscape(Landscape):
    """Use NK stuff to generate the landscape

    Actually, this is an extended NK landscape, as the each dimensions can
    have more the 2 (binary) discrete values

    """
    def __init__(self, dims, seed=None, K=0, cache_path=None):
        Landscape.__init__(self, dims, cache_path)  # Base class construction
        self.generate_parameter_fitnesses(seed, K)
        self.assign_patch_fitnesses()
        self.normalize_fitnesses()

    def __repr__(self):
        return "NKLandscape<dims:%s>" % (self.dims.dim_str())

    def generate_parameter_fitnesses(self, seed, K):
        """Generate fitnesses for the patches

        We have N parameters (dimensions)
        Each parameter can have S states, so (0, 1) for binary
        Each parameter state generates a fitness
        The total fitness is the average across all parameters

        K is how many other parameters (dimensions) each parameter relies on.
        Assume than we have 3 binary dimensions, A, B, C
        In the K == 0 case:
            For each parameter, we assign a random value to each state. For
            example:
                if A == 0 then .665
                if A == 1 then .123
            To get the value for the total state we average across all
            parameters

        In the K == 1 case:
            Each dimension is linked to one other dimension. The value for
            each state now depends on the state of another parameter. Assume A
            is linked to (relies on) B. The fitness for B can now take on 4
            different values, depending on the state of A and the state of B:
                if A == 0 and B == 0 then .667
                if A == 0 and B == 1 then .123
                if A == 1 and B == 0 then .492
                if A == 1 and B == 1 then .092
            Again, we average over all fitnesses

        """
        # Randomly link each of the N positions to K others
        numpy_random.seed(seed)
        N = self.dims.dimensionality()

        # The fitness of each parameter depends on itself and K other
        # parameters...
        dependencies = numpy.zeros((N, K + 1), int)
        # The first dependency is just yourself
        dependencies[:, 0] = numpy.arange(0, N)

        if K > 0:
            # Now add some random others. They can't be the same as the current
            # one though, so we generate numbers in range 0, N-1, then
            # adjust...
            # This almost does the right thing, but get repeats!
            # links = numpy_random.randint(0, N - 1, (N, K))
            # So ...
            links = numpy.zeros((N, K))
            for i in range(N):
                l = sample_without_repeats(N - 1, K)

                # Now we increment those that point to the same parameter
                # or more. This adjusts for the above N - 1 random number
                # generation
                links[i] = numpy.where(l >= i, l + 1, l)

            # Now add these to the dependencies
            dependencies[:, -K:] = links

        # Note that we can't use a numpy array here, as some dimensions
        # may differ in size...
        parameter_fitnesses = []

        # Go through each dimension and generate a set of values for it
        for i in range(N):
            # Get the sizes of the dependent axes for this parameter
            dnum = [self.dims.axes[d] for d in dependencies[i]]
            # Generate it using the same shape we'll need
            # TODO Should we use uniform random?
            parameter_fitnesses.append(numpy_random.uniform(0, 1, dnum))

        self.K = K
        self.dependencies = dependencies
        self.parameter_fitnesses = parameter_fitnesses

    def assign_patch_fitnesses(self):
        """Now assign each patch a fitness.

        This uses the dependencies generated above.
        """
        log.info("Assigning NK fitnesses to patches...")

        # We'll use these over and over
        ndims = self.dims.dimensionality()
        deps_and_fits = zip(self.dependencies, self.parameter_fitnesses)

        # TODO Should pbly swap the loops here. It might be faster...
        for p in self.patches.patch_array_flat:
            fit = 0.0
            # Get the values of the parameters representing these patches
            vals = p['values']

            # Get through each parameter
            for deps, fits in deps_and_fits:
                # The value depends on the current parameter and what it
                # depends on (see above). This extracts the relevant values
                # given our dependencies.
                relevant_values = vals[deps]

                # Now use "item" to index into the relevant fitness value
                f = fits.item(*relevant_values)
                fit += f

            # Assign the average
            p['fitness'] = fit / ndims

    def normalize_fitnesses(self):
        # TODO Now Normalise the fitnesses
        fit = self.data['fitness']
        minfit = min(fit)
        maxfit = max(fit)
        normed = (fit - minfit) * 1.0 / (maxfit - minfit)
        self.data['fitness'] = normed
