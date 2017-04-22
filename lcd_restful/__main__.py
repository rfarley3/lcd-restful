#!/usr/bin/env python
import sys
from getopt import getopt, GetoptError


USAGE = """\
Usage %s [-h|--help] [-f|--fake]
\t-h or --help\tThis help message
\t-f or --fake\tIf on RPi, use FakeHw

"""


def get_args(args):
    arg0 = args[0]
    try:
        opts, args = getopt(args[1:], 'hf', ['help', 'fake'])
    except GetoptError as e:
        print('GetoptError %s' % e)
        sys.exit(2)
    ret_args = {}
    ret_args['fake'] = False
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print(USAGE % arg0)
            sys.exit(0)
        elif opt in ['-f', '--fake']:
            ret_args['fake'] = True
        else:
            print(USAGE % arg0)
            sys.exit(1)
    return ret_args


def main_serv(clargs=sys.argv):
    opts = get_args(clargs)
    if opts['fake']:
        from . import override_rpigpio
        override_rpigpio()
    from .api import Server
    s = Server()
    s.run()
    return 0


if __name__ == "__main__":
    sys.exit(main_serv())

