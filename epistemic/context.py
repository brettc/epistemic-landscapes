import logging
log = logging.getLogger("context")

import pytreatments

import parameters
import analysis
import agent
import landscape


class Context(pytreatments.Context):

    def load_namespace(self, ns):
        ns['parameters'] = parameters.Parameters
        ns['landscape'] = self.landscape

        # We need to add the agent classes too...
        for cls in analysis.analyses:
            ns[cls.__name__] = cls

        for cls in agent.agent_classes:
            ns[cls.__name__] = cls

        self.defaults = {}

    def landscape(self, seed, k, dims):
        d = landscape.Dimensions(dims)
        l = landscape.NKLandscape(
            d, K=k, seed=seed, cache_path=self.config.cache_path)

        return l
