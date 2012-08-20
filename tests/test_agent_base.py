import basetest
import nose

from epistemic.agent_base import Blarg


def test_stuff():
    i = range(4)
    a = Blarg(i)
    print a.v
    assert a.v == i
    print a.s

if __name__ == '__main__':
    nose.runmodule(argv=['nose', '-s'])
