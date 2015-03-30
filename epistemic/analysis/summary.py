import logging
log = logging.getLogger("analysis.summary")

import csv

from .. import plugin
from .. import agent
from .. import stats
from ..simulation import Simulation


class Row(object):
    def __init__(self, sim):
        assert isinstance(sim, Simulation)
        self.sim = sim
        self.st = stats.Stats(sim.patch_controller.patches)

    @staticmethod
    def basic_headers():
        return """
            treatment
            replicate
        """.strip().split()

    # NOTE: the ordering above should match to what is below
    def basic_data(self):
        return [
            self.sim.treatment_name,
            str(self.sim.replicate_seq),
        ]

    @staticmethod
    def stats_headers():
        return """
            count
            coverage
            progress
            knowledge
        """.strip().split()

    def stats_data(self):
        return [
            len(self.sim.agents),
            self.st.coverage,
            self.st.progress,
            self.st.knowledge,
            ]

    @staticmethod
    def stats_agent_headers():
        snames = Row.stats_headers()
        anames = agent.get_agent_class_names()

        headers = []
        for nm in anames:
            for s in snames:
                headers.append("{}_{}".format(nm, s))
        return headers


    def stats_agent_data(self):
        counts = [0] * agent.agent_types
        for a in self.sim.agents:
            counts[a.typeid] += 1

        data = []
        for i in range(agent.agent_types):
            data.extend([
                counts[i],
                self.st.per_agent[i].coverage,
                self.st.per_agent[i].progress,
                self.st.per_agent[i].knowledge,
            ])

        return data

@plugin.register_plugin
class summary(plugin.Plugin):

    def begin_experiment(self):
        self.output_file = self.get_file('summary.csv')
        self.csv_writer = csv.writer(self.output_file)
        self.csv_writer.writerow(
            Row.basic_headers() +
            Row.stats_headers() +
            Row.stats_agent_headers()
        )

    def begin_simulation(self, sim):
        self.sim = sim

    def end_replicate(self):
        row = Row(self.sim)
        self.csv_writer.writerow(
            row.basic_data() +
            row.stats_data() +
            row.stats_agent_data()
        )
        self.output_file.flush()
