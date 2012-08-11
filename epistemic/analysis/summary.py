import logging
log = logging.getLogger("analysis.summary")

from base import ExperimentAnalysis, register_analysis
import numpy
import csv

import agent

class Row(object):
    def __init__(self, sim):
        self.treatment = sim.treatment.name
        self.replicate = sim.treatment.replicate

    @staticmethod
    def basic_headers():
        return """
            treatment
            replicate
        """.strip().split()

    # NOTE: the ordering above should match to what is below
    def basic_data(self):
        return [
            self.treatment,
            str(self.replicate),
        ]

    @staticmethod
    def agent_headers():
        return ['%s_count' % name for name in agent.get_agent_class_names()]

    # def agent_data(self):
        # for a in self.sim.agents:

        # return 

@register_analysis
class summary(ExperimentAnalysis):

    def begin_experiment(self):
        self.output_file = self.get_file('summary.csv')
        self.csv_writer = csv.writer(self.output_file)
        # self.csv_writer.writerow(['treatment','replicate','total_agents'])

    def end_replicate(self, sim):
        row = Row(sim)
        row.output(self.csv_writer)
        self.output_file.flush()

        # csv_writer.writerow([
            # self.treatment,
            # str(self.replicate),

