import logging
log = logging.getLogger("plugin")

import os

ANALYSED = 'ANALYSED'

CTX_NONE, CTX_EXPERIMENT, CTX_TREATMENT, CTX_REPLICATE = range(4)


class Plugin(object):

    # Default load priority
    priority = 5

    def __init__(self, config):
        self.config = config
        self.treatment = None
        self.replicate = None
        self.output_path = None
        self.context = CTX_NONE
        log.debug("Creating Plugin %s", self.name)

    def get_file(self, name, attr='wb'):
        pth = self.get_file_name(name)
        return open(pth, attr)

    def get_file_name(self, name):
        # Only make output folder when needed
        self.make_output_folder()
        pth = os.path.join(self.output_path, name)
        log.debug("Acquiring file name '%s'", pth)
        return pth

    def make_output_folder(self):
        if not os.path.exists(self.output_path):
            log.debug("Making folder '%s'", self.output_path)
            os.makedirs(self.output_path)

    @property
    def analysed_mark(self):
        self.make_output_folder()
        return os.path.join(self.output_path, ANALYSED)

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def experiment_output_path(self):
        basepth = self.config.experiment.output_path
        return os.path.join(basepth, self.name)

    @property
    def treatment_output_path(self):
        basepth = self.treatment.output_path
        return os.path.join(basepth, self.name)

    @property
    def replicate_output_path(self):
        basepth = self.replicate.output_path
        return os.path.join(basepth, self.name)

    def do_begin_experiment(self):
        # Run any user begin_experiment
        self.context = CTX_EXPERIMENT
        self.output_path = self.experiment_output_path
        if hasattr(self, 'begin_experiment'):
            log.info("Begin experiment processing for '%s'", self.name)
            self.begin_experiment()

    def do_begin_treatment(self, t):
        self.context = CTX_TREATMENT
        self.treatment = t
        self.output_path = self.treatment_output_path
        if hasattr(self, 'begin_treatment'):
            log.debug("plugin:'%s' begin_treatment" % self.name)
            self.begin_treatment()

    def do_begin_replicate(self, r):
        self.context = CTX_REPLICATE
        self.replicate = r
        self.output_path = self.replicate_output_path
        if hasattr(self, 'begin_replicate'):
            log.debug("plugin:'%s' begin_replicate..." % self.name)
            self.begin_replicate()

    def do_begin_simulation(self, sim):
        if hasattr(self, 'begin_simulation'):
            self.begin_simulation(sim)

    def do_end_simulation(self, sim):
        if hasattr(self, 'end_simulation'):
            self.end_simulation(sim)

    def do_analyse_replicate(self, history):
        if not hasattr(self, 'analyse_replicate'):
            return
        if os.path.exists(self.analysed_mark):
            if not self.config.args.reanalyse:
                log.info("Analysis '%s' already complete", self.name)
                return
            else:
                os.unlink(self.analysed_mark)

        log.info("Analysis '%s' running...", self.name)
        self.analyse_replicate(history)
        open(self.analysed_mark, 'a').close()

    def do_end_replicate(self):
        self.context = CTX_REPLICATE
        if hasattr(self, 'end_replicate'):
            log.debug("plugin:'%s' end_replicate..." % self.name)
            self.end_replicate()
        self.replicate = None

    def do_end_treatment(self):
        self.context = CTX_TREATMENT
        self.output_path = self.treatment_output_path
        if hasattr(self, 'begin_treatment'):
            log.debug("plugin:'%s' begin_treatment" % self.name)
            self.begin_treatment()
        self.treatment = None

    def do_end_experiment(self):
        self.context = CTX_EXPERIMENT
        self.output_path = self.experiment_output_path
        if hasattr(self, 'end_experiment'):
            log.info("End Experiment processing '%s'", self.name)
            self.end_experiment()

    def collate_csv(self, nm):
        """Collate all separate CSV files into one

        Works at experiment or treatment level
        """
        # TODO We're always re-analysing here. Maybe shouldn't?
        if os.path.exists(self.analysed_mark):
            log.debug("Removing %s", self.analysed_mark)
            os.unlink(self.analysed_mark)

        assert self.context in (CTX_EXPERIMENT, CTX_TREATMENT)
        collated = self.get_file(nm)

        # Dodgy get around of inner scoping
        firsttime = [True]
        success = [True]

        def collate_treatment(t):
            for r in t.replicates:
                if r.is_complete:
                    pth = os.path.join(r.output_path, self.name, nm)
                    f = open(pth)
                    if firsttime:
                        # Make false
                        firsttime.pop()
                    else:
                        # Discard headers after the first time
                        f.readline()
                    collated.write(f.read())
                elif not r.is_skipped:
                    log.warning("Can't collate everything as %s is missing", r)
                    if success:
                        success.pop()

        if self.context == CTX_TREATMENT:
            collate_treatment(self.treatment)
        else:
            for t in self.config.experiment.treatments:
                collate_treatment(t)

        if success:
            open(self.analysed_mark, 'a').close()


# This allows us to export them to the namespace in the config_loader
plugin_classes = set()


def register_plugin(a):
    global plugin_classes
    plugin_classes.add(a)
    return a
