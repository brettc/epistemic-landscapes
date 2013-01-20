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
import patches


# See here:
# http://numpy-discussion.10968.n7.nabble.com/Generating-random-samples-without-repeats-td25666.html
def sample_without_repeats(M, N):
    return numpy.random.rand(M).argsort()[:N]


class Landscape(object):
    """Maybe we'll manually define one later, so keep a base class"""
    def __init__(self, dims, cache_path=None):
        self.dims = dims
        self.patches = patches.Patches(dims, cache_path)

    def clear(self):
        self.patches.clear()

    @property
    def data(self):
        return self.patches.patch_array_flat

    def get_fitness(self):
        return self.data['fitness']

    def set_fitness(self, f):
        self.data['fitness'] = f

    fitness = property(get_fitness, set_fitness)

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
        self.finalize()

    def __repr__(self):
        return "NKLandscape<dims:%s>" % (self.dims.dim_str())

    def generate_parameter_fitnesses(self, seed, K):
        """Generate fitnesses for the patches

        We have N parameters (dimensions)
        Each parameter can have S states, so (0, 1) for binary
        Each parameter state generates a fitness
        The total fitness is the average across all parameters

        K is how many other parameters (dimensions) each parameter relies on.
        Assume than we have 3 binary dimensions, A, B, C. Total fitness depends
        on the value of these parameters which can take on A={0,1}, B= same same

        In the K == 0 case:
            For each parameter, we assign a random value to each state. As K =
            0, we assign a value to each possible state that A can take, which
            is 0 or 1. For example:
                if A == 0 then f(A) = .665
                if A == 1 then f(A) = .123
            To get the value for the total state we work out the same thing for
            B and C, then average across all parameters

        In the K == 1 case:
            Each dimension is linked to one other dimension. The value for
            each state now depends on the state of another parameter. Assume A
            is linked to (relies on) B. The fitness for B can now take on 4
            different values, depending on the state of A and the state of B.
            So assign 4 different random values to the A parameter. For
            example:
                if A == 0 and B == 0 then f(A) = .667
                if A == 0 and B == 1 then f(A) = .123
                if A == 1 and B == 0 then f(A) = .492
                if A == 1 and B == 1 then f(A) = .092
            That just gives us the fitness of parameter A. We'd do the same for
            B and C now. Then average.

        So the fitness of each parameter depends on itself, and K other
        parameters.  The higher K is, the more random values we need for each
        parameter.
        """
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
            # TODO Think about whether we we use uniform random?
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

    def finalize(self):
        self.normalize_volume()

    def normalize_fitness(self):
        fit = self.data['fitness']
        minfit = min(fit)
        maxfit = max(fit)
        normed = (fit - minfit) * 1.0 / (maxfit - minfit)
        self.data['fitness'] = normed

    def normalize_volume(self):
        fit = self.data['fitness']
        total = sum(fit)
        self.data['fitness'] = fit / total

    def raise_water(self, proportion_to_cover=.5):
        if proportion_to_cover <= 0.0 or proportion_to_cover >= 1.0:
            log.error("The proportion_to_cover should be greater than zero and less "
                      "that 1.0, you've set it to %s", proportion_to_cover)
            raise RuntimeError
        fit = self.data['fitness']
        cutoff = int(round(proportion_to_cover * len(fit)))

        # Sort and find the max amount we want
        fitsort = numpy.sort(fit)
        maxsize = fitsort[cutoff - 1]

        # Now set everything else to zero and finalize
        newfit = numpy.where(fit <= maxsize, 0.0, fit)

        self.data['fitness'] = newfit
        self.finalize()

    def squish_bottom(self, squish_from, squish_to, scaling=1.0):
        """
        Squishes the points in a box of height 'squish_from' into a box of
        height 'squish_to'. So anything that was 0.0 will become squish_to.
        Anything above squish_from stays the same.

        Linear scaling = 1.0. Use higher to curve the
        scaling so you don't get a hard edge.
        """
        if squish_from <= 0.0 or squish_from > 1.0:
            log.error("Squish squish_from should be greater than zero and less "
                      "that 1.0, you've set it to %s", squish_from)
            raise RuntimeError

        # TODO: could make this stretch too...?
        if squish_from <= squish_to:
            log.error("squish_from needs to be great than squish_to")
            raise RuntimeError

        self.normalize_fitness()
        fit = self.data['fitness']
        # We only affect everything below squish_from
        lower_indexes = numpy.where(fit < squish_from)
        lower = fit[lower_indexes]

        # Non linear scaling -- just a power, as it is easy.
        # The higher the scaling, the more curvy the top end is.
        if scaling != 0.0:
            lower = pow(lower, scaling)

        # remap everything, and apply
        lower = squish_to + (lower * ((squish_from - squish_to) / squish_from))
        fit[lower_indexes] = lower

        # Need to renormalize, cos now the lowest value is squish_to
        self.finalize()

    def fast_find_peaks(self):
        n = self.data['neighbours']
        f = self.data['fitness']
        # Where is the fitness always greater than the neighbours?
        return numpy.where(f > f[n].max(axis=1))[0]

    def find_peaks(self):
        peaks = []
        for p in self.patches.patch_array_flat:
            bestf = p['fitness']
            for neighbour_i in p['neighbours']:
                otherp = self.patches.patch_array_flat[neighbour_i]
                otherf = otherp['fitness']
                if otherf > bestf:
                    break
            else:
                # Ok, we got here, so no others are better
                peaks.append(p['index'])
        return peaks
