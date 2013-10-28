import logging
log = logging.getLogger("analysis.series")

from ..pytreatments import plugin

import numpy
import csv

# TODO: Add these back in
has_rpy = False
has_pyx = False

# try:
    # from rpy2.robjects.packages import importr
    # from rpy2.robjects import DataFrame, IntVector, FloatVector
    # import rpy2.robjects.lib.ggplot2 as g2
    # has_rpy = True
# except:
#   has_pyx = False

# try:
#     from pyx import *
#
#     # Let's use some nice fonts -- I hate the default shite Latex stuff
#     # Not xetex unfortunately...
#     text.set(mode="latex")
#     text.preamble(r"""\renewcommand{\familydefault}{\sfdefault}""")
#     text.preamble(r"""\usepackage{amsmath}""")
#     text.preamble(r"""\usepackage{cmbright}""")
#     has_pyx = True
#
# except:
#     has_pyx = False


@plugin.register_plugin
class series(plugin.Plugin):

    def begin_simulation(self, sim):
        self.sim = sim
        self.agent_types = sim.agent_types()
        self.dtype = numpy.dtype([
            # Timestep
            ('t', numpy.int32),
            ('explored', numpy.float64),
            ('explored_by_type', numpy.float64, len(self.agent_types))
            ])

    def begin_replicate(self):
        # Preallocate the array
        self.data = numpy.zeros(sim.parameters.max_steps, self.dtype)

    def step(self, sim):
        """Gather all the series data"""
        record = self.data[sim.time_step]
        record['t'] = sim.time_step
        self.calc_explored(record, sim)
        self.calc_explored_by_type(record, sim)


    def end_replicate(self, sim):
        f = self.get_file('series.csv')

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
        # if has_pyx:
        #     self.create_pyx_graph()

    def calc_explored(self, record, sim):
        """How much of the total space is currently explored?"""
        # Where returns a tuple when only a condition is spec'd. Just grab the
        # first bit...
        explored = numpy.where(sim.landscape['visits'] > 0)[0]

        # Just compare it to total space
        fraction = float(len(explored)) / float(len(sim.landscape))
        record['explored'] = fraction

    def calc_explored_by_type(self, record, sim):
        # Make a set of all visited cells for each type
        visited = []
        for nm, i in self.agent_types:
            x = numpy.where(sim.landscape['visits_by_type'][:,i] > 0)[0]
            visited.append(float(len(x))/float(len(sim.landscape)))

        record['explored_by_type'][:] = visited


    def create_pyx_graph(self):
        fname = self.get_file_name("series.pdf")
        g = graph.graphxy(width=12,
                        x=graph.axis.linear(min=0, max=len(self.data)),
                        y=graph.axis.linear(min=0, max=1),
                        key=graph.key.key(pos="tl", dist=0.1))

        # TODO fix this shitty stuff up
        names = [n.lower() for n, i in self.agent_types]
        plts = [graph.data.values(title='explored', x=self.data['t'], y=self.data['explored'])]
        for i, n in enumerate(names):
            plts.append(graph.data.values(title=n, x=self.data['t'], y=self.data['explored_by_type'][:,i]))
        g.plot(plts, [graph.style.line([color.gradient.Rainbow])])

        g.writePDFfile(fname)
        log.info("Made a graph in '%s'", fname)


    def create_rpy_graph(self):
        fname = self.get_file_name("series_rpy.pdf")

        names = [n.lower() for n, i in self.agent_types]
        types = [(names[n], FloatVector(self.data['explored_by_type'][:, n]))
                 for n in range(len(names))]
        dct = dict(types)
        dct.update({
            't': FloatVector(self.data['t']+1),
            'explored': FloatVector(self.data['explored']),
        })

        dataf = DataFrame(dct)

        grdevices = importr('grDevices')
        grdevices.pdf(file=fname)
        gp = g2.ggplot(dataf)

        gp += g2.geom_line(g2.aes_string(x='t', y='explored'))
        for n in names:
            gp += g2.geom_line(g2.aes_string(x='t', y=n))

        gp.plot()
        grdevices.dev_off()

        log.info("Made a graph in '%s'", fname)

