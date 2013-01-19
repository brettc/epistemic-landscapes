from basetest import pytest
import numpy
import itertools

from epistemic.landscape import NKLandscape
from epistemic.dimensions import Dimensions

# Simple tests


def test_redimension():
    d = Dimensions()
    d.add_dimensions(4, 4)
    d.add_dimensions(2, 4)
    l = NKLandscape(d, K=0)
    x = l.data
    # This should work
    x.shape = d.axes


def test_boolean_dimensions():
    d = Dimensions()
    d.add_dimensions(2, 5)
    assert d.axes == [2] * 5


# Test everything for a range of dimension from little to big
test_dimensions = [
    ((2, 4), (4, 4)),
    # ((2, 8), (3, 2)),
    ((2, 12),),
]

# Test K for different values
all_k = range(4)

# Test both against each other
test_nk = [x for x in itertools.product(test_dimensions, all_k)]


@pytest.fixture(params=test_dimensions, scope="module")
def f_dimensions(request):
    """Generate a bunch of different dimensions for testing landscapes"""
    dims = Dimensions()
    for d in request.param:
        dims.add_dimensions(*d)
    return dims


# TODO Something is wrong here -- they're getting created every time!
@pytest.fixture(params=test_nk, scope='module')
def f_landscape(request):
    """Generate Landscapes from the various dimensions"""
    dims, k = request.param
    return NKLandscape(Dimensions(dims), K=k)


@pytest.fixture
def f_tiny_landscape():
    """A small landscape for fast tests"""
    d = Dimensions()
    d.add_dimensions(2, 5)
    return NKLandscape(d)


def test_dependencies(f_landscape):
    deps = f_landscape.dependencies
    for i, d in enumerate(deps):
        # The first set should be the same as the index
        selfd = d[0]
        assert selfd == i
        # And the others should not be the same!!
        for v in d[1:]:
            assert v != i


def test_neighbourhood(f_landscape):
    # Now check that the neighbours are what we think
    parray = f_landscape.patches.patch_array_flat

    for p in parray:
        vals = numpy.array(p['values'])
        for n in p['neighbours']:
            neigh_vals = numpy.array(parray[n]['values'])

            # Should differ by 1, cos it's a neighbour
            assert sum(vals != neigh_vals) == 1


def test_squishing(f_landscape):
    # Not really testing ....
    f_landscape.squish_bottom(.5, .4, 3)


def test_bad_waterline(f_tiny_landscape):
    with pytest.raises(RuntimeError):
        f_tiny_landscape.raise_water(-.2)
    with pytest.raises(RuntimeError):
        f_tiny_landscape.raise_water(0.0)
    with pytest.raises(RuntimeError):
        f_tiny_landscape.raise_water(1.0)
    with pytest.raises(RuntimeError):
        f_tiny_landscape.raise_water(1.1)


def test_waterline(f_landscape):
    f_landscape.raise_water(proportion_to_cover=.5)
    fit = f_landscape.fitness
    zeros = numpy.where(fit == 0.0)[0]

    assert len(zeros) == len(fit) / 2
    assert abs(sum(f_landscape.fitness) - 1.0) < 1e-5



@pytest.mark.xfail(reason="don't know")
def test_peaks(f_landscape):
    assert set(f_landscape.find_peaks()) == set(f_landscape.fast_find_peaks())

if __name__ == '__main__':
    pytest.main(__file__)
