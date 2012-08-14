from basetest import *
import numpy

from nose.plugins.attrib import attr
from epistemic.landscape import NKLandscape
from epistemic.dimensions import Dimensions

def test_boolean_dimensions():
    d = Dimensions() 
    d.add_dimensions(2, 5)
    assert d.axes == [2] * 5

def test_neighbourhood():
    d = Dimensions()
    d.add_dimensions(4, 4)
    d.add_dimensions(2, 4)

    landscape = NKLandscape(d)

    # Now check that the neighbours are what we think
    parray = landscape.patches.patch_array_flat

    for p in parray:
        vals = numpy.array(p['values'])
        for n in p['neighbours']:
            neigh_vals = numpy.array(parray[n]['values'])

            # Should differ by 1, cos it's a neighbour
            assert sum(vals != neigh_vals) == 1

def _check_deps(ls):
    deps = ls.dependencies
    for i, d in enumerate(deps):
        # The first set should be the same as the index
        selfd = d[0]
        assert selfd == i
        # And the others should not be the same!!
        for v in d[1:]:
            assert v != i

def test_dependencies():
    d = Dimensions()
    d.add_dimensions(4, 4)
    d.add_dimensions(2, 4)

    # TODO Repeat this !!
    l = NKLandscape(d, K=0)
    _check_deps(l)
    l = NKLandscape(d, K=1)
    _check_deps(l)
    l = NKLandscape(d, K=2)
    _check_deps(l)

def test_redimension():
    d = Dimensions()
    d.add_dimensions(4, 4)
    d.add_dimensions(2, 4)
    l = NKLandscape(d, K=0)
    x = l.data
    # This should work
    x.shape = d.axes

if __name__ == '__main__':
    nose.runmodule()
    # unittest.main()
