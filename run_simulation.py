import logging
log = logging.getLogger("main")

import sys
from epistemic import context, simulation, main

if __name__ == "__main__":
    sys.exit(main.run_main(
        simulation.Simulation,
        context.Context,
        None,
        progress=None
    ))


