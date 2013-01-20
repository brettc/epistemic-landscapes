# from .. import basetest
import os
import fnmatch
# import pytest

from epistemic.pytreatments import script, config
from epistemic import context, simulation

HERE = os.path.abspath(os.path.dirname(__file__))


def get_scripts():
    names = os.listdir(HERE)
    names = fnmatch.filter(names, "*.cfg")
    return names


def pytest_generate_tests(metafunc):
    # This function feeds the output of the above function into the tests below
    if 'script_name' in metafunc.fixturenames:
        metafunc.parametrize("script_name", get_scripts())


def test_scripts(script_name):
    pth = os.path.join(HERE, script_name)
    cfg = config.Configuration(simulation.Simulation, True)
    ctx = context.Context(cfg)
    sct = script.Script(ctx)
    sct.load(pth)
    cfg.experiment.run(None)
