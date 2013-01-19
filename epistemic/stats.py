import logging
log = logging.getLogger("stats")

# Mostly operations on landscapes.
def percent_visited_above_x(patch_data, cutoff, agent_typeid=None):
    assert cutoff > 0.0 and cutoff < 1.0
    fitness = patch_data['fitness']

    # Check out how easy numpy makes this kind of operation
    # We get an array of booleans back
    higher_than_cutoff = fitness > cutoff

    if agent_typeid is None:
        visit_count = patch_data['visits']
    else:
        visit_count = patch_data['visits_by_type'][:,agent_typeid]

    visited = visit_count > 0

    visited_above_cutoff = visited & higher_than_cutoff

    # How much is above the cutoff in total
    fit_total = sum(fitness[higher_than_cutoff] - cutoff)

    # How much of this has been visited
    fit_visited = sum(fitness[visited_above_cutoff] - cutoff)

    pc_visited = fit_visited/fit_total
    return pc_visited

