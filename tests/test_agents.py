from basetest import pytest

from epistemic import landscape, dimensions, simulation, agent, parameters


@pytest.fixture
def small_landscape():
    d = dimensions.Dimensions()
    d.add_dimensions(4, 4)
    d.add_dimensions(2, 4)
    return landscape.NKLandscape(d)


@pytest.fixture
def tiny_sim(small_landscape):
    p = parameters.Parameters(
        seed=1,
        landscape=small_landscape,
        max_steps=10,
    )
    p.add_agents(agent.Maverick, 5)
    p.add_agents(agent.Drunk, 5)
    p.add_agents(agent.Follower, 5)
    s = simulation.Simulation(0, "Test", 0, p)
    return s


def test_agents(tiny_sim):
    # This is what the experiment framework does...
    tiny_sim.begin()
    tiny_sim.run()

    # What happened to our agents?
    assert len(tiny_sim.agents) == 15
    for a in tiny_sim.agents:
        assert len(a.visited) > 0


if __name__ == "__main__":
    pytest.main(__file__)
