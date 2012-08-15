import logging
log = logging.getLogger("main")

from epistemic import config, script, context, experiment, simulation

cfg = config.Configuration(True)

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


def load():
    global cfg
    # configure_logging()
    script_path = 'examples/summary.cfg'
    ctx = context.Context(cfg)
    sct = script.Script(ctx)
    sct.load(script_path)

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

