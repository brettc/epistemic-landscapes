import logging
log = logging.getLogger("experiment")
import os

import random

RUNNING = "RUNNING"
COMPLETE = "COMPLETE"
SEED = "SEED"
SKIPPED = "SKIPPED"


class Interrupt(Exception):
    """Use this to stop an experiment"""
    pass


class Experiment(object):
    def __init__(self, config):
        self.config = config
        self.name = None
        self.treatments = []
        self.current_treatment = None
        self.loaded_plugins = []
        self.treatment_names = set()

        # We use this to generates seeds for all of the experiments
        self.rand = random.Random()

    def set_seed(self, seed):
        self.rand.seed(seed)

    def add_treatment(self, name, replicates, **kwargs):
        if name in self.treatment_names:
            log.error("Treatment with name '%s' already exists", name)
            return

        self.treatment_names.add(name)

        log.info(
            "Adding treatment '%s' to Experiment '%s', with %d replicates",
            name, self.name, replicates)

        # We give each treatment its own derivative seed to maintain
        # consistency within a treatment if we change the replicate number
        tseed = self.rand.randint(0, 1 << 32)
        self.treatments.append(Treatment(self, name, replicates, tseed, **kwargs))

    def get_replicate(self, name, rep_num):
        # Look up the treatment
        for t in self.treatments:
            if t.name == name:
                break
            else:
                log.warning("Treatment %s not found", name)
            return None

        # Now the replicate
        try:
            r = t.replicates[rep_num]
        except IndexError:
            log.warning("Replicate {} of Treatment {} not found".format(name, rep_num))
            return None

        return r

    def load_plugin(self, plugin_cls, kwargs):
        """Add some plugin to run both during and after the simulation"""

        # Filter if we ask for a specific plugin
        p = self.config.args.plugin
        if p is not None:
            if p != plugin_cls.__name__:
                log.info("Ignoring plugin: '{0.__name__}'".format(plugin_cls))
                return

        log.info("Loading plugin: priority {0.priority}, name '{0.__name__}'".format(
            plugin_cls))
        self.loaded_plugins.append((plugin_cls, kwargs))

    def order_by_priority(self):
        self.loaded_plugins.sort(key=lambda x: x[0].priority)

    def run_begin(self):
        text = "Begin Experiment:'{}'".format(self.name)
        log.info("{:=^78}".format(text))
        self.output_path = self.config.output_path
        # open(self.experiment_mark, 'a').close()

    def run_end(self):
        text = "End Experiment:'{}'".format(self.name)
        log.info("{:=^78}".format(text))
        # os.unlink(self.experiment_mark)

    def run(self, progress):

        callbacks = []
        plugins = []

        # Order everything by the class priority. This sort out dependencies
        # between the different plugins
        self.order_by_priority()

        # Create All Plugins
        for plugin_cls, kwargs in self.loaded_plugins:
            c = plugin_cls(self.config, **kwargs)
            plugins.append(c)
            if hasattr(c, 'step'):
                callbacks.append(c.step)

        self.run_begin()

        for c in plugins:
            c.do_begin_experiment()

        for t in self.treatments:
            # Skip to desired treatment
            if self.config.args.treatment is not None:
                if t.name != self.config.args.treatment:
                    continue

            self.current_treatment = t
            t.run(plugins, callbacks, progress)

        self.current_treatment = None

        for c in plugins:
            c.do_end_experiment()

        self.run_end()

    @staticmethod
    def make_path(pth):
        if not os.path.exists(pth):
            log.debug("Making path %s", pth)
            os.makedirs(pth)


class Treatment(object):
    def __init__(self, experiment, name, rcount, tseed, **kwargs):
        self.experiment = experiment
        self.name = name
        self.replicate_count = rcount
        self.extra_args = kwargs
        self.rand = random.Random()
        self.rand.seed(tseed)
        rfun = self.experiment.rand.randint
        self.replicates = [Replicate(experiment, self, i, rfun(0, 1 << 32))
                           for i in range(self.replicate_count)]

    def run(self, plugins, callbacks, progress=None):
        self.output_path = os.path.join(self.experiment.output_path, self.name)
        self.text = "Experiment:'{0}' Treatment:'{1}'".format(
            self.experiment.name, self.name)
        log.info("{:=^78}".format(""))
        log.info("{: ^78}".format(self.text))

        # Run begin and end to setup plugin for running
        for c in plugins:
            c.do_begin_treatment(self)

        for r in self.replicates:
            r.run(plugins, callbacks, progress)

        for c in plugins:
            c.do_end_treatment()


class Replicate(object):
    def __init__(self, experiment, treatment, r, seed):
        self.experiment = experiment
        self.treatment = treatment
        self.sequence = r
        self.seed = seed

    @property
    def is_complete(self):
        return os.path.exists(self.complete_mark)

    @property
    def is_skipped(self):
        return os.path.exists(self.skipped_mark)

    @property
    def running_mark(self):
        return os.path.join(self.output_path, RUNNING)

    @property
    def complete_mark(self):
        return os.path.join(self.output_path, COMPLETE)

    @property
    def seed_mark(self):
        return os.path.join(self.output_path, SEED)

    @property
    def skipped_mark(self):
        return os.path.join(self.output_path, SKIPPED)

    @property
    def output_path(self):
        return os.path.join(self.treatment.output_path,
                            "{:0>3}".format(self.sequence))

    def run(self, plugins, callbacks, progress):
        # We can run a single replicate if required
        if self.experiment.config.args.replicate is not None:
            if self.experiment.config.args.replicate != self.sequence:
                    return

        text = "{0} Rep:{1:0>3} ({2:}/{3:}), using Seed:{4:}".format(
            self.treatment.text,
            self.sequence,
            self.sequence + 1,
            self.treatment.replicate_count,
            self.seed)
        log.info("{:-^78}".format(""))
        log.info("{: ^78}".format(text))

        for c in plugins:
            c.do_begin_replicate(self)

        # Run the simulation if required
        if not self.is_complete:
            # Are we just doing an analysis?
            if not self.experiment.config.args.analysis:
                self.run_simulation(plugins, callbacks, progress)
            else:
                log.info("Not running Simulation %03d (analysis only).",
                         self.sequence)
        else:
            log.info("Simulation %03d already successfully run.",
                     self.sequence)

        # Now analyse the simulation
        self.analyse_simulation(plugins)

        for c in plugins:
            c.do_end_replicate()

    def run_simulation(self, plugins, callbacks, progress):
        log.info("{:.^78}".format("Running Simulation"))
        self.experiment.make_path(self.output_path)
        open(self.running_mark, 'a').close()
        s = open(self.seed_mark, 'a')
        s.write("%s" % self.seed)
        s.close()

        # Finally, we actually create a simulation
        sim = self.experiment.config.sim_class(
            seed=self.seed,
            treatment_name=self.treatment.name,
            replicate_seq=self.sequence,
            **self.treatment.extra_args
        )

        # We can skip a simulation if we don't begin
        if not sim.begin():
            # If the history is safely closed, we can now say we're done
            os.unlink(self.running_mark)
            open(self.skipped_mark, 'a').close()
            log.info("Skipping replicate, as begin return False...")
            return

        # Create a history class if we have one.
        if self.experiment.config.history_class is not None:
            history_cls = self.experiment.config.history_class
            history = history_cls(self.output_path, sim)
        else:
            history = None

        for c in plugins:
            c.do_begin_simulation(sim)

        # Actually run the simulation. Here is where the action is.
        sim.run(history, callbacks, progress)

        for c in plugins:
            c.do_end_simulation(sim)

        # This might help shut some stuff down, before running the unloading...
        if history is not None:
            history.close()

        # If the history is safely closed, we can now say we're done
        os.unlink(self.running_mark)
        open(self.complete_mark, 'a').close()

    def analyse_simulation(self, plugins):
        # Put this warning at the beginning
        log.info("{:.^78}".format(""))
        log.info("{: ^78}".format("Analysing Simulation"))
        history = self.get_history()
        if history is None:
            return

        for c in plugins:
            c.do_analyse_replicate(history)
        history.close()

    def get_history(self):
        history_cls = self.experiment.config.history_class
        if history_cls is None:
            # log.warning("No analysis possible as there no history class")
            return None

        if not os.path.exists(self.complete_mark):
            log.info("Can't Analyse Incomplete Simulation")
            return None

        # Load the history
        history_cls = self.experiment.config.history_class
        history = history_cls(self.output_path, replicate_seed=self.seed)
        return history

