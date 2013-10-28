import logging
log = logging.getLogger("main")

import sys
from optparse import OptionParser
from epistemic.pytreatments import run_main
from epistemic import context, simulation

import epistemic.analysis
if __name__ == "__main__":
    sys.exit(run_main(
        simulation.Simulation,
        context.Context,
        history=None,
        progress=None
    ))


