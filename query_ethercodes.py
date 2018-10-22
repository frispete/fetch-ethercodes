#! /usr/bin/env python3
"""
Synopsis:
Query manufacturer from arpwatch {ecfile}

Usage: {appname} [-hVv] [-e file] ethercode..
       -h, --help           this message
       -V, --version        print version and exit
       -v, --verbose        verbose mode (cumulative)
       -e, --ec file        use file as ethercode source

ethercode: at least 3 colon separated, hexadecimal bytes of an ethernet
           address, e.g.: 90:e6:ba, 00:1B:21, ...

Notes: {appname} tries to read {ecfile} from these locations:
       {locations}


Copyright:
(c)2018 by {author} {email}

License:
{license}
"""
#
# vim:set et ts=8 sw=4:
#

__version__ = '0.1'
__author__ = 'Hans-Peter Jansen'
__email__ = '<hpj@urpla.net>'
__license__ = 'MIT'


import os
import sys
import time
import getopt
import traceback

# avoid encoding issues with print() in locale-less environments
os.environ["PYTHONIOENCODING"] = "utf-8"

class gpar:
    """ global parameter class """
    appdir, appname = os.path.split(sys.argv[0])
    if appdir == '.':
        appdir = os.getcwd()
    pid = os.getpid()
    version = __version__
    author = __author__
    email = __email__
    license = __license__
    loglevel = 0
    force = False
    keep = False
    timestamp = False
    deltat = 2.5
    ecfile = 'ethercodes.dat'
    locations = ['.', appdir, '/usr/share/arpwatch']


def vout(lvl, msg, file = sys.stdout):
    if lvl <= gpar.loglevel:
        print((msg).format(**gpar.__dict__), file = file, flush = True)

stderr = lambda *msg: print(*msg, file = sys.stderr, flush = True)

def exit(ret = 0, msg = None, usage = False):
    """ terminate process with optional message and usage """
    if msg:
        stderr('{}: {}'.format(gpar.appname, msg.format(**gpar.__dict__)))
    if usage:
        stderr(__doc__.format(**gpar.__dict__))
    sys.exit(ret)


hex = lambda x: int(x, 16)
hexstr = lambda h: format(h, 'x')

def code_key(val):
    """ return the colon formated code key, if val is an exact 24 byte
        hexadecimal string, and None otherwise
        000000 -> 0:0:0
        ABCDEF -> ab:cd:ef
    """
    if len(val) == 6:
        return ':'.join((map(hexstr, map(hex, (val[:2], val[2:4], val[4:])))))


def decode_key(val):
    """ return the ethercode from a colon formatted hexadecimal str,
        ab:cd:ef -> 11259375 (0xabcdef)
    """
    v1, v2, v3 = val.split(':')[:3]
    return (hex(v1) << 16) + (hex(v2) << 8) + hex(v3)


def load_ecfile(ecfile):
    vout(1, 'load {ecfile}')
    start = time.time()
    codes = {}
    ln = 0
    with open(ecfile, newline = '', encoding = 'utf-8') as f:
        for l in f:
            ln += 1
            try:
                code, manufacturer = l.rstrip().split('\t')
            except ValueError as e:
                stderr('invalid format in line #{}: {}'.format(ln, l))
            else:
                ec = decode_key(code)
                vout(3, '{}: {}: {}'.format(ec, code, manufacturer))
                if ec in codes:
                    vout(2, '{} exists already: {}'.format(ec, codes[ec]))
                codes[ec] = manufacturer

    vout(1, '{} codes loaded in {:.2f} sec.'.format(len(codes), time.time() - start))
    return codes


def query_ethercodes(args):
    # load etherodes.dat file
    ecfile = gpar.ecfile
    codes = {}
    vout(2, 'locate {ecfile}')
    if os.path.exists(ecfile):
        codes = load_ecfile(ecfile)
    else:
        for loc in gpar.locations:
            ecpath = os.path.join(loc, ecfile)
            vout(2, 'locate {}'.format(ecpath))
            if os.path.exists(ecpath):
                codes = load_ecfile(ecpath)
                break
    if not codes:
        exit(2, 'failed to load any valid {ecfile} file from {locations}')

    for arg in args:
        try:
            ec = decode_key(arg)
        except ValueError as e:
            stderr('invalid ethernet code: {}: {}'.format(arg, e))
        else:
            vout(0, '{}: {}'.format(arg, codes.get(ec, 'UNKNOWN')))

    return 0


def main(argv = None):
    if argv is None:
        argv = sys.argv[1:]

    # yeah, oldschool, I know...
    try:
        optlist, args = getopt.getopt(argv, 'hVve:',
            ('help', 'version', 'verbose', 'ecfile')
        )
    except getopt.error as msg:
        exit(1, msg, True)

    for opt, par in optlist:
        if opt in ('-h', '--help'):
            exit(usage = True)
        elif opt in ('-V', '--version'):
            exit(msg = 'version %s' % gpar.version)
        elif opt in ('-v', '--verbose'):
            gpar.loglevel += 1
        elif opt in ('-e', '--ecfile'):
            gpar.ecfile = ecfile

    try:
        query_ethercodes(args)
    except Exception:
        exit(2, 'unexpected exception occured:\n%s' % traceback.format_exc())


if __name__ == '__main__':
    sys.exit(main())
