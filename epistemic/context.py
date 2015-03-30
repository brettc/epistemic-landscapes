import logging
log = logging.getLogger("context")

import parameters
import agent
import landscape
import dimensions
import plugin
import placement
import analysis # Force loading

class Context(object):
    def __init__(self, config):
        self.config = config

        # This namespace controls what you see in the script
        ns = {}
        ns['add_treatment'] = self.add_treatment
        ns['load_plugin'] = self.load_plugin
        ns['get_replicate'] = self.get_replicate
        ns['seed'] = self.set_seed
        ns['output'] = self.set_output

        ns['parameters'] = parameters.Parameters
        ns['landscape'] = landscape.NKLandscape
        ns['dimensions'] = dimensions.Dimensions

        for cls in agent.agent_classes:
            ns[cls.__name__] = cls

        for cls in placement.placement_classes:
            ns[cls.__name__] = cls

        # Load the plugin class into the namespace
        for p in plugin.plugin_classes:
            ns[p.__name__] = p

        self.namespace = ns

    def init(self, pth):
        self.config.init_from_script(pth)

    def set_output(self, pth):
        log.info("The script is setting the output_path to '%s'", pth)
        self.config.set_base_path(pth)

    def set_seed(self, seed):
        log.info("Setting the experiment random seed to %s", seed)
        self.config.experiment.set_seed(seed)

    def add_treatment(self, name, replicates=1, **kwargs):
        # Duplicate the parameters so that they can't be changed
        self.config.experiment.add_treatment(name, replicates, **kwargs)

    def get_replicate(self, name, rep_num):
        return self.config.experiment.get_replicate(name, rep_num)

    def load_plugin(self, cls, **kwargs):
        if cls not in plugin.plugin_classes:
            log.error("Ignoring unknown plugin %s", str(cls))
        else:
            self.config.experiment.load_plugin(cls, kwargs)
