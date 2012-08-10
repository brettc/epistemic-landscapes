import logging
log = logging.getLogger("analysis.summary")

from base import ExperimentAnalysis, register_analysis
import numpy
import csv

@register_analysis
class summary(ExperimentAnalysis):

    def begin_experiment(self):
        self.output_file = self.get_file('summary.csv')
        self.csv_writer = csv.writer(f)
        self.csv_writer.writerow(['treatment','size'])

    def end_replicate(self, sim):
        pass

            # csv_writer.writerow([
                # row['t'],
                # row['explored']
            # ] + vals)

    def end_experiment(self):
        pass


