import logging
log = logging.getLogger("script")

import os
import traceback
import sys
import cStringIO


class ScriptError(Exception):
    pass


class Script(object):
    def __init__(self, context):
        self.context = context

    def load(self, pth):
        pth = os.path.expanduser(pth)
        pth = os.path.normpath(pth)
        if not os.path.exists(pth) or \
                not os.path.isfile(pth):
            log.error("The script file '%s' does not exist", pth)
            raise RuntimeError

        # We need to set some stuff in the Experiment first
        self.context.config.set_script(pth)

        # ... then execute this (which can change the config)
        self.execute(pth)

        # Now continue the initialisation
        self.context.config.init()

    def execute(self, pth):
        try:
            log.info("{:-<78}".format("Begin Loading Script %s" % pth))
            execfile(pth, self.context.namespace)

        # TODO This is WAY too complex. Make it nicer
        except SyntaxError, err:
            log.error("Syntax error in loading script '%s'", pth)
            log.error("Line %d", err.lineno)
            log.error("%s", err.text[:-1])
            if err.offset > 1:
                log.error("%s^", (' ' * (err.offset - 1)))
            else:
                log.error("^")
            raise ScriptError(err)
        except Exception, err:
            # Stolen from logging. It's rubbish. But it will do for now.
            ei = sys.exc_info()
            sio = cStringIO.StringIO()
            traceback.print_exception(ei[0], ei[1], ei[2], None, sio)
            s = sio.getvalue()
            sio.close()
            if s[-1:] == "\n":
                s = s[:-1]
            log.error("Unhandled exception in loading script: '%s'", pth)
            log.error(s)
            raise ScriptError(err)

        log.info("{:-<78}".format("Finished Loading Script %s" % pth))
