import logging
log = logging.getLogger("landscape")
# import 
import numpy
import numpy.random as numpy_random
import operator
import itertools
import os
import cPickle as pickle
import agent

from patches import Patches

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
        Landscape.__init__(self, dims, cache_path) # Base class construction
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
        dependencies = numpy.zeros((N, K+1), int)
        # The first dependency is just yourself
        dependencies[:,0] = numpy.arange(0, N)

        if K > 0:
            # Now add some random others. They can't be the same as the current
            # one though, so we generate numbers in range 0, N-1, then
            # adjust...
            # FIXME This is still not right, cos we can get repeats!
            # Need to do a "sample"
            links = numpy_random.randint(0, N-1, (N, K))

            # Now we increment those that point to the same parameter or more
            # This adjust for the above N-1 random number generation
            for i in range(N):
                links[i] = numpy.where(links[i] >= i, links[i]+1, links[i])

            # Now add these to the dependencies
            dependencies[:,-K:] = links

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
        normed = (fit - minfit) * 1.0/(maxfit-minfit)
        self.data['fitness'] = normed

