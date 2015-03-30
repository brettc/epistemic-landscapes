import logging
log = logging.getLogger("main")

import sys
import os
import argparse

import config
import script
import simulation


def get_parser():
    parser = argparse.ArgumentParser(description='Run the simulation.')
    parser.add_argument("script", metavar="<script>",
                        help="A python script file")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true", dest="verbose",
        help="show verbose (debug) output")

    parser.add_argument(
        "-o", "--output", type=str,
        help="Provide a base folder for output (overrides script definition)")

    parser.add_argument(
        "-R", "--redo-analyses", action="store_true", dest="reanalyse",
        help="Redo the analyses (only with the analysis option)")

    parser.add_argument(
        "--dont-ask", action="store_true", dest="dont_ask",
        help="Don't ask for verification on deletion, just do it")

    parser.add_argument(
        "--treatment", type=str, dest="treatment",
        help="Just do a specific treatment")
    parser.add_argument(
        "--replicate", type=int, dest="replicate",
        help="Just do a specific replicate")
    parser.add_argument(
        "--plugin", type=str, dest="plugin",
        help="Just run a particular plugin")

    # Mutually exclusive options about what to do with existing stuff
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--continue",
        action="store_true", dest="keepgoing",
        help="Continue an existing experiment")
    group.add_argument(
        "--analysis",
        action="store_true", dest="analysis",
        help="Analyse an existing experiment")
    group.add_argument(
        "--restart",
        action="store_true", dest="restart",
        help="Restart the experiment (losing any previous output)")
    return parser


def configure_logging():
    # TODO Add additional logger in the output folder
    handler = logging.StreamHandler(sys.stdout)
    # format = "%(name)-15s | %(levelname)-8s | %(asctime)s | %(message)s"
    format = "%(name)-20s | %(levelname)-8s | %(message)s"
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    root = logging.getLogger("")
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def run_main(sim_class, context_class, history_class=None, progress=None, parser=get_parser()):
    configure_logging()
    args = parser.parse_args()

    # We should have one argument: the folder to read the configuration from
    if not args:
        # Otherwise exit, printing the help
        parser.print_help()
        return 2

    script_path = args.script

    # If there's no extension, add it
    root, ext = os.path.splitext(script_path)
    if ext == "" or ext == ".":
        script_path = root + '.cfg'

    log.info("{:=<78}".format("Starting up"))

    # Load, using the first argument as the folder
    cfg = config.Configuration(sim_class, history_class, args)
    ctx = context_class(cfg)
    spt = script.Script(ctx)

    # For now, we just turn on debugging
    if args.verbose:
        logging.getLogger("").setLevel(logging.DEBUG)

    try:
        spt.load(script_path)
        cfg.experiment.run(progress)

    except KeyboardInterrupt:
        log.error("User interrupted the Program")
    except simulation.Interrupt:
        # An error should already have been printed
        pass

    return 1
