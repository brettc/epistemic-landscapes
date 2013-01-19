import logging
log = logging.getLogger("context")

import pytreatments

import parameters
import analysis
import agent
import landscape
import dimensions


class Context(pytreatments.Context):

    def load_namespace(self, ns):
        ns['parameters'] = parameters.Parameters
        ns['landscape'] = self.landscape

        for cls in agent.agent_classes:
            ns[cls.__name__] = cls

        self.defaults = {}

    def landscape(self, seed, k, dims):
        d = dimensions.Dimensions(dims)
        l = landscape.NKLandscape(
            d, K=k, seed=seed, cache_path=self.config.cache_path)

        return l
