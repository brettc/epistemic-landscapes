import logging
log = logging.getLogger("main")
from optparse import OptionParser
import sys
from epistemic import config, script, context, experiment, simulation

cfg = config.Configuration(True)

def configure_options():
    usage = """usage: python %prog [options] <config-file>"""
    parser = OptionParser(usage)
    # parser.add_option(
        # "-v", "--verbose",
        # action="store_true", dest="verbose",
        # help="show verbose (debug) output")
    # parser.add_option(
        # "-c", "--clean",
        # action="store_true", dest="clean",
        # help="Clean any previous output")
    # parser.add_option(
        # "-g", "--graphics=",
        # type="int", dest="graphics", default=0, metavar="N",
        # help="show graphics every N steps")

    return parser

def load():
    global cfg
    parser = configure_options()
    options, args = parser.parse_args()
    ctx = context.Context(cfg)
    sct = script.Script(ctx)
    sct.load(args[0])

def run():
    global cfg
    cfg.experiment.run(None)

if __name__ == "__main__":
    import cProfile, pstats
    # Well behaved unix programs exits with 0 on success...
    load()
    cProfile.run('run()', 'profile.output')
    p = pstats.Stats('profile.output')
    p.sort_stats('time').print_stats(20)
    # p.strip_dirs().sort_stats(-1).print_stats()

