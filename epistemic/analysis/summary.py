import logging
log = logging.getLogger("analysis.summary")

from base import ExperimentAnalysis, register_analysis
import numpy
import csv

import agent, stats

class Row(object):
    def __init__(self, sim):
        self.sim = sim
        self.treatment = sim.treatment.name
        self.replicate = sim.treatment.replicate

    @staticmethod
    def basic_headers():
        return """
            treatment
            replicate
            coverage
        """.strip().split()

    # NOTE: the ordering above should match to what is below
    def basic_data(self):

        pc = stats.percent_visited_above_x(
            self.sim.landscape.data, 
            self.sim.parameters.significance_cutoff)
        return [
            self.treatment,
            str(self.replicate),
            pc,
        ]

    @staticmethod
    def agent_headers():
        return ['%s_count' % name for name in agent.get_agent_class_names()]

    # def agent_data(self):
        # for a in self.sim.agents:


@register_analysis
class summary(ExperimentAnalysis):

    def begin_experiment(self):
        self.output_file = self.get_file('summary.csv')
        self.csv_writer = csv.writer(self.output_file)
        self.csv_writer.writerow(Row.basic_headers() + Row.agent_headers())

    def end_replicate(self, sim):
        row = Row(sim)
        self.csv_writer.writerow(row.basic_data())
        self.output_file.flush()


