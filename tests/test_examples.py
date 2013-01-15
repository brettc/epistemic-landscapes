# from basetest import *

# from epistemic import config, script, context, experiment, simulation

# EXAMPLE_PATH = os.path.join(ROOT_PATH, 'examples')

# # We grab the name of the path from the function name. A bit sneaky, but it
# # avoids screwing up function name / folder correspondence. See here:
# # http://code.activestate.com/recipes/66062-determining-current-function-name/
# def path_from_function():
    # # get name of the caller function (up 1 level in stack frame)
    # funcname = sys._getframe(1).f_code.co_name
    # # Remove 'test_'
    # cfg_name = funcname[5:] + '.cfg'
    # return cfg_name

# def load_cfg_and_run(name):
    # pth = os.path.join(EXAMPLE_PATH, name)
    # cfg = config.Configuration(True) # Clean up

    # ctx = context.Context(cfg)
    # spt = script.Script(ctx)
    # spt.load(pth)
    # cfg.experiment.run(None)

# # NOTE We could get all of these automatically, but declaring makes it easier
# # to play with individual details
# def test_basic():
    # load_cfg_and_run(path_from_function())

# @attr('testing')
# def test_summary():
    # load_cfg_and_run(path_from_function())

# if __name__ == '__main__':
    # nose.runmodule()
