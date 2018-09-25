#! /usr/bin/env python3
"""
Synopsis:

Fetch current IEEE MA-L Assignments file (oui.csv) from IEEE.org,
and generate ethercodes.dat for arpwatch consumption.

Usage: {appname} [-hVvfT][-t sec][-O ouifile][-o outfile]
       -h, --help           this message
       -V, --version        print version and exit
       -v, --verbose        verbose mode (cumulative)
       -f, --force          force operation
       -T, --timestamp      print timestamp
       -t, --deltat sec     tolerance in timestamp comparison
                            (default: {deltat} sec.)
       -O, --ouifile file   IEEE.org host
                            (default: {ouifile})
       -o, --outfile file   arpwatch ethercodes
                            (default: {outfile})

Description:
Fetch oui.csv only, if the timstamp is newer (unless --force is given).
Similar, generate ethercodes.dat only, if the timestamp don't match
(again, unless --force is given).

Notes:
The timestamps of oui.csv fluctuate in a 2 seconds range(!). Therefore
compensate the fluctuation by taking a deltat tolerance factor into
account.

Copyright:
(c)2016 by {author}

License:
{license}
"""
#
# vim:set et ts=8 sw=4:
#

__version__ = '0.1'
__author__ = 'Hans-Peter Jansen <hpj@urpla.net>'
__license__ = 'GNU GPL v2 - see http://www.gnu.org/licenses/gpl2.txt for details'


import os
import csv
import sys
import time
import getopt
import traceback
import email.utils
import urllib.error
import urllib.parse
import urllib.request


class gpar:
    """ global parameter class """
    appdir, appname = os.path.split(sys.argv[0])
    if appdir == '.':
        appdir = os.getcwd()
    pid = os.getpid()
    version = __version__
    author = __author__
    license = __license__
    loglevel = 0
    force = False
    timestamp = False
    ouifile = 'http://standards-oui.ieee.org/oui/oui.csv'
    outfile = 'ethercodes.dat'
    deltat = 2.5


def vout(lvl, msg):
    if lvl <= gpar.loglevel:
        print((msg).format(**gpar.__dict__), file = sys.stdout, flush = True)

stderr = lambda *msg: print(*msg, file = sys.stderr, flush = True)

def exit(ret = 0, msg = None, usage = False):
    """ terminate process with optional message and usage """
    if msg:
        stderr('{}: {}'.format(gpar.appname, msg))
    if usage:
        stderr(__doc__.format(**gpar.__dict__))
    sys.exit(ret)


def cmp_ts(t1, t2):
    """ compare timestamps while taking a global tolerance factor into
        account
        return True, if timestamps match
    """
    return abs(t1 - t2) < gpar.deltat


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


def main():
    ret = 0
    vout(2, 'started with pid {pid} in {appdir}')
    vout(1, 'check {ouifile}')
    req = urllib.request.urlopen(gpar.ouifile)
    vout(2, 'header info: {}'.format(req.info()))
    header = req.info()
    ouisize = int(header['Content-Length'])
    vout(1, 'oui file size: {}'.format(ouisize))
    ouidate = header['Last-Modified']
    vout(1, 'oui file date: {}'.format(ouidate))
    ouidate = email.utils.parsedate(ouidate)
    ouitime = time.mktime(ouidate)
    vout(3, 'parsed oui file date: {} ({})'.format(
            time.asctime(ouidate), ouitime))

    # extract file argument of URL (used to be 'oui.csv')
    infile = os.path.basename(urllib.parse.urlparse(req.geturl()).path)
    gpar.infile = infile
    # check, if local oui.csv is outdated
    fetchoui = False
    if gpar.force:
        fetchoui = True
    elif not os.path.exists(infile):
        vout(1, 'no local file {} found'.format(infile))
        fetchoui = True
    elif os.path.getsize(infile) != ouisize:
        vout(1, 'local file size differ: {} vs. {} remote'.format(
                os.path.getsize(infile), ouisize))
        fetchoui = True
    elif not cmp_ts(os.stat(infile).st_mtime, ouitime):
        vout(3, str(os.stat(infile).st_mtime))
        vout(3, str(ouitime))
        mtime = time.localtime(os.stat(infile).st_mtime)
        otime = time.localtime(ouitime)
        vout(1, 'local file date differ: {} vs. {} remote'.format(
                time.asctime(mtime), time.asctime(otime)))
        fetchoui = True
    # fetch oui.csv
    if fetchoui:
        vout(1, 'fetch {ouifile}')
        open(infile, 'wb').write(req.read())
        os.utime(infile, (ouitime, ouitime))

    # check, if ethercodes.dat is outdated
    outfile = gpar.outfile
    gencodes = False
    if gpar.force:
        gencodes = True
    elif not os.path.exists(outfile):
        vout(1, 'no local file {} found'.format(outfile))
        gencodes = True
    elif not cmp_ts(os.stat(outfile).st_mtime, ouitime):
        vout(3, str(os.stat(outfile).st_mtime))
        vout(3, str(ouitime))
        mtime = time.localtime(os.stat(outfile).st_mtime)
        otime = time.localtime(ouitime)
        vout(2, 'local file date differ: {} vs. {} remote'.format(
                time.asctime(mtime), time.asctime(otime)))
        gencodes = True

    # generate ethercodes.dat
    if gencodes:
        vout(1, 'parse {infile}')
        codes = {}
        with open(infile, newline = '') as f:
            reader = csv.reader(f)
            rows = 0
            for row in reader:
                vout(3, str(row))
                # generate
                code = code_key(row[1])
                if code:
                    if code in codes and codes[code] != row[2]:
                        vout(1, 'value {} exists already: "{}", "{}"'.format(
                                code, codes[code], row[2]))
                    else:
                        codes[code] = row[2]
                rows += 1

        vout(1, 'generate {} with {} entries'.format(outfile, len(codes)))
        with open(outfile, 'w') as f:
            for key in sorted(codes.keys()):
                f.write('%s\t%s\n' % (key, codes[key]))
        os.utime(outfile, (ouitime, ouitime))
        vout(1, 'successful')
    else:
        vout(1, 'code file {} up to date already'.format(outfile))

    if gpar.timestamp:
        vout(0, time.strftime('%Y%m%d-%H%M%S', ouidate))

    return ret


if __name__ == '__main__':
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'hVvfTt:O:o:',
            ('help', 'version', 'verbose', 'force', 'timestamp',
             'deltat', 'ouifile', 'outfile')
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
        elif opt in ('-f', '--force'):
            gpar.force = True
        elif opt in ('-T', '--timestamp'):
            gpar.timestamp = True
        elif opt in ('-t', '--deltat'):
            gpar.deltat = par
        elif opt in ('-O', '--ouifile'):
            gpar.ouifile = par
        elif opt in ('-o', '--outfile'):
            gpar.outfile = par

    try:
        sys.exit(main())
    except Exception:
        exit(2, 'unexpected exception occured:\n%s' % traceback.format_exc())
