import logging
log = logging.getLogger("config")
import os
import shutil
from experiment import Experiment
from simulation import Interrupt


class Configuration(object):
    """This holds the user configuration info"""

    def __init__(self, sim_class, history_class, args, name=None):
        self.sim_class = sim_class
        self.history_class = history_class
        self.args = args
        self.base_path = None
        self.script_path = None
        self.name = name
        self.analysis_only = False
        self.experiment = Experiment(self)

    def set_script(self, pth):
        self.script_path = pth
        base_path, name = os.path.split(pth)
        name, ext = os.path.splitext(name)
        self.base_path = base_path
        self.experiment.name = name

    def set_base_path(self, pth):
        # This is set above, but the script can override it
        self.base_path = pth

    def init(self):
        """Call this one if you're doing it programmatically"""

        # Modify the base_path if we're told to
        if self.args.output is not None:
            self.base_path = self.args.output

        self.base_path = os.path.expanduser(self.base_path)
        self.base_path = os.path.normpath(self.base_path)
        if not os.path.exists(self.base_path):
            log.error("Base path '%s' does not exist", self.base_path)
            raise RuntimeError

        self.make_experiment_folder(self.experiment.name + '.output')
        self.init_logger(self.output_path)

        if self.script_path:
            # We're going to stick a copy of the script into the output folder.
            # This is good for referring to later
            log.info("Saving copy of script '%s' to '%s'",
                     self.script_path, self.output_path)
            shutil.copy(self.script_path, self.output_path)

    ## {{{ http://code.activestate.com/recipes/541096/ (r1)
    @staticmethod
    def confirm(prompt=None, resp=False):
        """prompts for yes or no response from the user. Returns True for yes and
        False for no.

        'resp' should be set to the default value assumed by the caller when
        user simply types ENTER.

        >>> confirm(prompt='Create Directory?', resp=True)
        Create Directory? [y]|n:
        True
        >>> confirm(prompt='Create Directory?', resp=False)
        Create Directory? [n]|y:
        False
        >>> confirm(prompt='Create Directory?', resp=False)
        Create Directory? [n]|y: y
        True

        """

        if prompt is None:
            prompt = 'Confirm'

        if resp:
            prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
        else:
            prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')

        while True:
            ans = raw_input(prompt)
            if not ans:
                break
            if ans not in ['y', 'Y', 'n', 'N']:
                print 'please enter y or n.'
                continue
            if ans == 'y' or ans == 'Y':
                resp = True
                break
            if ans == 'n' or ans == 'N':
                resp = False
                break

        # Get rid of line
        print
        return resp

    def make_experiment_folder(self, pth):
        pth = os.path.join(self.base_path, pth)

        if os.path.exists(pth):
            if os.path.isdir(pth):
                # We already have an experiment. Users must be explicit about
                # what to do.
                if self.args.restart:
                    if not self.args.dont_ask:
                        resp = self.confirm("Are you sure you want remove everything in '%s'" % pth)
                    else:
                        resp = True
                    if resp:
                        log.info("Removing existing experiment in '%s' and "
                                "restarting", pth)
                        shutil.rmtree(pth)
                    else:
                        raise Interrupt

                elif self.args.keepgoing:
                    log.info("Continuing the experiment already in '%s'", pth)

                elif self.args.analysis:
                    log.info("Analysing existing experiment in '%s'", pth)
                    self.analysis_only = True

                else:
                    log.error("An experiment already exists in '%s'. ", pth)
                    log.error("You must specify whether to restart, "
                              "continue, or analyse the existing experiment")
                    raise Interrupt
            else:
                log.error("Cannot create folder '%s'", pth)
                raise RuntimeError

        # We might have deleted the folder
        if not os.path.exists(pth):
            os.mkdir(pth)
            log.info("Created folder '%s'", pth)

        self.output_path = pth
        log.info("Setting output folder to '%s'", self.output_path)

    @staticmethod
    def init_logger(pth):
        log_path = os.path.join(pth, "log.txt")
        handler = logging.FileHandler(log_path, 'a')
        formatter = logging.Formatter(
            "%(levelname)-8s | %(asctime)s | %(name)-15s | %(message)s")
        handler.setFormatter(formatter)

        # Actually, let's keep it trim...
        handler.setLevel(logging.WARNING)
        logging.getLogger("").addHandler(handler)
        logging.getLogger("reporting").addHandler(handler)

        log.info("Full output log can be found in '%s'", log_path)
