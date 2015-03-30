## {{{ http://code.activestate.com/recipes/572182/ (r2)
import sys
import termios
import atexit
from select import select

# save the terminal settings
try:
    fd = sys.stdin.fileno()
except:
    pass
new_term = termios.tcgetattr(fd)
old_term = termios.tcgetattr(fd)

# new terminal setting unbuffered
new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)

# switch to normal terminal

def set_normal_term():
    termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)

# switch to unbuffered terminal

atexit.register(set_normal_term)
termios.tcsetattr(fd, termios.TCSAFLUSH, new_term)


def putch(ch):
    sys.stdout.write(ch)


def getch():
    return sys.stdin.read(1)


def getche():
    ch = getch()
    putch(ch)
    return ch


def kbhit():
    dr, dw, de = select([sys.stdin], [], [], 0)
    return dr != []

if __name__ == '__main__':

    while 1:
        if kbhit():
            ch = getch()
            break
        sys.stdout.write('.')

    print 'done'
## end of http://code.activestate.com/recipes/572182/ }}}
