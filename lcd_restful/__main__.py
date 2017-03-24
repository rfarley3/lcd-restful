#!/usr/bin/env python
import sys
from getopt import getopt, GetoptError
from .api import Server
from .fake import FakeLcdApi


USAGE = """\
Usage %s [-h|--help]
\t-h or --help\tThis help message

"""


def get_args(args):
    try:
        opts, args = getopt(args[1:], 'hf', ['help', 'fake'])
    except GetoptError as e:
        print('GetoptError %s' % e)
        sys.exit(2)
    ret_args = {}
    ret_args['fake'] = False
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print(USAGE % args[0])
            sys.exit(0)
        elif opt in ['-f', '--fake']:
            ret_args['fake'] = True
        else:
            print(USAGE % args[0])
            sys.exit(1)
    return ret_args


def main_serv(clargs=sys.argv):
    opts = get_args(clargs)
    lcd = None
    if opts['fake']:
        lcd = FakeLcdApi()
    s = Server(lcd=lcd)
    s.run()
    return 0


if __name__ == "__main__":
    sys.exit(main_serv())
