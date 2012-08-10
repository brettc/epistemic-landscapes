import logging
log = logging.getLogger("analysis.summary")

from base import ExperimentAnalysis, register_analysis
import numpy
import csv

@register_analysis
class summary(ExperimentAnalysis):

    def summarize(self):
        f = self.get_file('summary.csv')

        for t in self.experiment.treatments:
            for s in t.simulations:
            x = numpy.where(sim.landscape['visits_by_type'][:,i] > 0)[0]




        csv_writer = csv.writer(f)
        csv_writer.writerow(['treatment','size'])
        for nm, sz in zip(treatment_name, clump_size):
            csv_writer.writerow([nm, sz])

        # TODO automate this using dtypes...
        csv_writer = csv.writer(f)
        names = [n.lower() for n, i in self.agent_types]
        csv_writer.writerow(['t', 'explored'] + names)
        for i, row in enumerate(self.data):
            vals = list(row['explored_by_type'])
            csv_writer.writerow([
                row['t'],
                row['explored']
            ] + vals)

        # if has_rpy:
            # self.create_rpy_graph()
