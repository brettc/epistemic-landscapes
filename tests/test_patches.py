from basetest import pytest

from epistemic import dimensions, patches, patch_control

#@pytest.fixture
#def small_landscape():
#    d = dimensions.Dimensions()
#    d.add_dimensions(4, 4)
#    d.add_dimensions(2, 4)
#    return landscape.NKLandscape(d)
#
#
#@pytest.fixture
#def tiny_sim(small_landscape):
#    p = parameters.Parameters(
#        seed=1,
#        landscape=small_landscape,
#        max_steps=10,
#        )
#    p.add_agents(agent.Maverick, 5)
#    p.add_agents(agent.Drunk, 5)
#    p.add_agents(agent.Follower, 5)
#    s = simulation.Simulation(p)
#    return s

def test_patches():
    d = dimensions.Dimensions()
    d.add_dimensions(2, 8)
    d.add_dimensions(3, 2)
    ps = patches.Patches(d)
    pc = patch_control.PatchController(ps)
    print pc[0].neighbours


if __name__ == "__main__":
    pytest.main(__file__)
