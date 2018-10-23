#! /usr/bin/env python3
"""
Synopsis:
Query manufacturer from arpwatch {ecfile}

Usage: {appname} [-hVv] [-e file] ethercode..
       -h, --help           this message
       -V, --version        print version and exit
       -v, --verbose        verbose mode (cumulative)
       -e, --ec file        use file as ethercode source
                            [default: {ecfile}]

ethercode: at least 3 hexadecimal bytes of an ethernet address,
        e.g.: 90:e6:ba, 00-1B-21, bytes must be separated with
        some non alpha numeric characters.

If no manufacturer was found, UNKNOWN is returned.

Notes: {appname} tries to read {ecfile} from these locations:
       {locations}.

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
import re
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
    ecfile = 'ethercodes.dat'
    locations = ['.', appdir, '/usr/share/arpwatch']


def vout(lvl, msg):
    if lvl <= gpar.loglevel:
        print((msg).format(**gpar.__dict__), file = sys.stdout, flush = True)
        return True
    return False

stderr = lambda *msg: print(*msg, file = sys.stderr, flush = True)

def exit(ret = 0, msg = None, usage = False):
    """ terminate process with optional message and usage """
    if msg:
        stderr('{}: {}'.format(gpar.appname, msg.format(**gpar.__dict__)))
    if usage:
        stderr(__doc__.format(**gpar.__dict__))
    sys.exit(ret)

hex = lambda x: int(x, 16)

def decode_key(val):
    """ return the ethercode from a hexadecimal str
        accept any separator, that is not alpha numeric
        ab:cd:ef -> 11259375 (0xabcdef)
    """
    # extract our separators
    sep = ''.join(set((c for c in val if not c.isalnum())))
    # split val by separators, and convert hex value
    ec = tuple(map(hex, re.split('[' + re.escape(sep) + ']', val)[:3]))
    # sanity check
    if max(ec) > 255:
        raise ValueError('hex values must be 0 <= val <= 255: %s' % str(ec))

    return (ec[0] << 16) + (ec[1] << 8) + ec[2]


def load_ecfile(ecfile):
    vout(2, 'load {ecfile}')
    start = time.time()
    codes = {}
    ln = 0
    with open(ecfile, newline = '', encoding = 'utf-8') as f:
        for l in f:
            ln += 1
            try:
                ec, manufacturer = l.rstrip().split('\t')
            except ValueError:
                stderr('invalid format in line #{}: {}'.format(ln, l))
            else:
                key = decode_key(ec)
                vout(3, '{}: {}: {}'.format(key, ec, manufacturer))
                if ec in codes:
                    vout(2, '{} exists already: {}'.format(ec, codes[key]))
                codes[key] = manufacturer

    vout(2, '{} codes loaded in {:.3f} sec.'.format(len(codes), time.time() - start))
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
            if os.path.exists(ecpath):
                codes = load_ecfile(ecpath)
                break
    if not codes:
        exit(2, 'failed to load a valid {ecfile} file from {locations}')

    for arg in args:
        try:
            ec = decode_key(arg)
        except ValueError as e:
            stderr('invalid ethernet code: {}: {}'.format(arg, e))
        else:
            manufacturer = codes.get(ec, 'UNKNOWN')
            if not vout(1, '{}: {}'.format(arg, manufacturer)):
                vout(0, manufacturer)

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
            gpar.ecfile = par

    try:
        query_ethercodes(args)
    except Exception:
        exit(2, 'unexpected exception occurred:\n%s' % traceback.format_exc())


if __name__ == '__main__':
    sys.exit(main())
