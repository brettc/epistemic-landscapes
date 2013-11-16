from basetest import pytest

from epistemic import dimensions, patches, patch_control, stats

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

def assert_close_enough(a, b):
    assert abs(a - b) < 1e-8


def test_progress():
    d = dimensions.Dimensions()
    d.add_dimensions(2, 8)
    ps = patches.Patches(d)
    assert ps.size == 256
    pc = patch_control.PatchController(ps)

    for i, p in enumerate(pc):
        # Make each patch have the same amount of fitness/knowledge
        p.fitness = .1

    for i, p in enumerate(pc):
        # This doesn't make any sense, but it will do for testing
        if i < 128:
            p.visits_by_type[0] = 1

        if i < 64:
            p.visits = 1
            p.visits_by_type[1] = 1

    st = stats.Stats(ps)
    assert_close_enough(st.coverage, .25)
    assert_close_enough(st.per_agent[0].total, .5)
    assert_close_enough(st.per_agent[1].total, .25)
    assert_close_enough(st.knowledge, .1 * 64)
    assert_close_enough(st.per_agent[0].knowledge, .1 * 128)
    # assert_close_enough(st.knowledge_gained_percent, .25)


if __name__ == "__main__":
    pytest.main(__file__)
