import logging
log = logging.getLogger("dimensions")

import operator

class Dimensions(object):
    """Represents the dimensions of the space"""
    def __init__(self, dim_tuples=[]):
        self.axes = []
        self.axes_by_size = {}

        # What if we're given just a single tuple?
        if len(dim_tuples) == 2:
            sz, hm = tuple(dim_tuples)
            if type(sz) is type(1) and type(hm) is type(1):
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
        return reduce(operator.add, [x-1 for x in self.axes])

    def size(self):
        return reduce(operator.mul, self.axes)

    def dim_str(self):
        ax = self.axes_by_size.items()
        ax.sort()
        return '-'.join(['%sx%s' % (k, v) for k, v in ax])

