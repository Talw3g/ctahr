

DEFAULT = '\033[49m\033[39m'
RED = '\033[91m'
BRED = '\033[101m'
DRED = '\033[107m\033[41m'
BLUE = '\033[94m'
DBLUE = '\033[107m\033[44m'
GREEN = '\033[92m'
DGREEN = '\033[107m\033[42m'
YELLOW = '\033[93m'
GREY = '\033[90m'

def ctxt(txt,color):
    return ''.join((color,txt,DEFAULT))
