import logging
log = logging.getLogger("main")

import sys
from optparse import OptionParser
import epistemic.pytreatments
from epistemic.pytreatments import config, script, plugin
from epistemic import context, simulation

import epistemic.analysis

def configure_options():
    usage = """usage: python %prog [options] <config-file>"""
    parser = OptionParser(usage)
    parser.add_option(
        "-v", "--verbose",
        action="store_true", dest="verbose",
        help="show verbose (debug) output")
    parser.add_option(
        "-c", "--clean",
        action="store_true", dest="clean",
        help="Clean any previous output")
    # parser.add_option(
        # "-g", "--graphics=",
        # type="int", dest="graphics", default=0, metavar="N",
        # help="show graphics every N steps")

    return parser


def configure_logging():
    # TODO Add additional logger in the output folder
    handler = logging.StreamHandler(sys.stdout)
    # format = "%(name)-15s | %(levelname)-8s | %(asctime)s | %(message)s"
    format = "%(name)-15s | %(levelname)-8s | %(message)s"
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    root = logging.getLogger("")
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def main():
    configure_logging()
    parser = configure_options()
    options, args = parser.parse_args()

    # We should have one argument: the folder to read the configuration from
    if not args:
        # Otherwise exit, printing the help
        parser.print_help()
        return 2

    script_path = args[0]
    log.info("Starting up...")

    # Load, using the first argument as the folder
    cfg = config.Configuration(simulation.Simulation, options.clean)
    ctx = context.Context(cfg)
    sct = script.Script(ctx)

    # For now, we just turn on debugging
    if options.verbose:
        logging.getLogger("").setLevel(logging.DEBUG)

    if sct.load(script_path):
        # TODO cfg.validate()
        p = None

        try:
            cfg.experiment.run(p)
            return 0

        except KeyboardInterrupt:
            log.error("User interrupted the Program")
        except epistemic.pytreatments.Interrupt:
            pass

    return 1

if __name__ == "__main__":
    # Well behaved unix programs exits with 0 on success...
    sys.exit(main())
