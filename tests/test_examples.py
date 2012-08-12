from basetest import *
import os, shutil, glob

from epistemic import config, script, context, experiment, simulation

EXAMPLE_PATH = os.path.join(TEST_PATH, 'examples')

def load_cfg_and_run(name):
    pth = os.path.join(EXAMPLE_PATH, name)
    cfg = config.Configuration(True) # Clean up

    try:
        ctx = context.Context(cfg)
        spt = script.Script(ctx)
        spt.load(pth)
        cfg.experiment.run(None)
    finally:
        # Always do this
        shutil.rmtree(cfg.output_path)

def test_all_analyses():
    match = os.path.join(EXAMPLE_PATH, "*.cfg")
    for f in glob.glob(match):
        yield load_cfg_and_run, f

if __name__ == '__main__':
    nose.runmodule()
