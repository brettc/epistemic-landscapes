from basetest import *
import numpy

from epistemic.landscape import Dimensions, NKLandscape

class TestLandscapes(TestCase):

    def test_boolean_dimensions(self):
        d = Dimensions() 
        d.add_dimensions(2, 5)
        self.assertEqual(d.axes, [2] * 5)

    def test_neighbourhood(self):
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

    def _check_deps(self, ls):
        deps = ls.dependencies
        for i, d in enumerate(deps):
            # The first set should be the same as the index
            selfd = d[0]
            self.assertEqual(selfd, i)
            # And the others should not be the same!!
            for v in d[1:]:
                self.assertNotEqual(v, i)

    def test_dependencies(self):
        d = Dimensions()
        d.add_dimensions(4, 4)
        d.add_dimensions(2, 4)

        # TODO Repeat this !!
        l = NKLandscape(d, K=0)
        self._check_deps(l)
        l = NKLandscape(d, K=1)
        self._check_deps(l)
        l = NKLandscape(d, K=2)
        self._check_deps(l)



if __name__ == '__main__':
    unittest.main()
