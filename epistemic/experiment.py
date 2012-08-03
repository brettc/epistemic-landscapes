import logging
log = logging.getLogger("experiment")

from simulation import Simulation
from analysis import TreatmentAnalysis, ReplicateAnalysis, ExperimentAnalysis
# from results import Results
import random

class Treatment(object):
    def __init__(self, experiment, name, rcount, parameters):
        self.experiment = experiment
        self.name = name
        self.replicate = None
        self.replicate_count = rcount
        self.parameters = parameters
        self.simulations = []

    def run(self, e_callbacks, progress=None):

        # Let the analyses set themselves up
        t_analyses = []
        callbacks = e_callbacks[:]
        for cls in self.experiment.treatment_analyses:
            c = cls(self.experiment.config, self) 
            if hasattr(c, 'setup'):
                c.setup()
            t_analyses.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        # Run all the replicates
        for i in range(self.replicate_count):
            self.replicate = i
            self.run_replicate(callbacks[:], progress)
        
        for a in t_analyses:
            if hasattr(a, 'summarize'):
                a.summarize()

    def run_replicate(self, callbacks, progress):
        log.info("Beginning Treatment '%s', replicate %d of %d", 
                 self.name,
                 self.replicate+1,
                 self.replicate_count)

        sim = Simulation(self.parameters)

        r_analyses = []
        for cls in self.experiment.replicate_analyses:
            c = cls(self.experiment.config, self)
            if hasattr(c, 'setup'):
                c.setup(sim)
            r_analyses.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        sim.run(callbacks, progress)
        self.simulations.append(sim)

        for a in r_analyses:
            if hasattr(a, 'summarize'):
                a.summarize(sim)

class Experiment(object):
    def __init__(self, config, name):
        self.config = config
        self.name = name
        self.seed = random.seed()

        self.treatments = []

        self.replicate_analyses = []
        self.treatment_analyses = []
        self.experiment_analyses = []

    def add_treatment(self, name, replicates, parameters):
        log.info("Adding treatment '%s', with %d replicates", name, replicates)
        self.treatments.append(Treatment(self, name, replicates, parameters))

    @property
    def dimensions(self):
        """Dimensions needed to store experiment-wide results"""
        dim1 = len(self.treatments)
        dim2 = max([t.replicates for t in self.treatments])
        return dim1, dim2

    def add_analysis(self, analyses_cls):
        """Add some analyses to run both during and after the simulation"""
        # if ExperimentAnalysis in analyses_cls.__subclasses__():
        log.info("Adding analysis '%s' to experiment", analyses_cls.__name__)
        if issubclass(analyses_cls, TreatmentAnalysis):
            self.treatment_analyses.append(analyses_cls)
        if issubclass(analyses_cls, ReplicateAnalysis):
            self.replicate_analyses.append(analyses_cls)
        if issubclass(analyses_cls, ExperimentAnalysis):
            self.experiment_analyses.append(analyses_cls)

    def run(self, progress):
        callbacks = []
        e_analyses = []
        for cls in self.experiment_analyses:
            c = cls(self.experiment.config, self) 
            if hasattr(c, 'setup'):
                c.setup()
            e_analyses.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        for t in self.treatments:
            t.run(callbacks, progress)
        
        for a in e_analyses:
            if hasattr(a, 'summarize'):
                a.summarize()

