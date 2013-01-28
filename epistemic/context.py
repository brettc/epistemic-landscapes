import logging
log = logging.getLogger("context")

import pytreatments

import parameters
import agent
import landscape
import dimensions
import placement
import analysis # Force loading


class Context(pytreatments.Context):

    def load_namespace(self, ns):
        ns['parameters'] = parameters.Parameters
        ns['landscape'] = landscape.NKLandscape
        ns['dimensions'] = dimensions.Dimensions

        for cls in agent.agent_classes:
            ns[cls.__name__] = cls

        for cls in placement.placement_classes:
            ns[cls.__name__] = cls
