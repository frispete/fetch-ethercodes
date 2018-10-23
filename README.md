Summary
=======

Fetch and generate ethercodes data for arpwatch.

Description
-----------
Fetch current IEEE MA-L Assignments file (oui.csv) from IEEE.org,
and generate ethercodes.dat for arpwatch consumption.

Fetch oui.csv only, if the timestamp is newer (unless --force is given).
Similar, generate ethercodes.dat only, if the timestamps don't match
(again, unless --force is given). Use option --keep to (re)generate
ethercodes.dat from an existing oui.csv.

Notes
-----
The timestamps of oui.csv fluctuate in a 2 seconds range(!). Therefore
compensate the fluctuation by taking a deltat tolerance factor into
account.

Usage
-----

```
Usage: fetch-ethercodes.py [-hVvfkt][-T sec][-O ouifile][-o outfile][-p spec]
       -h, --help           this message
       -V, --version        print version and exit
       -v, --verbose        verbose mode (cumulative)
       -f, --force          force operation
       -k, --keep           keep existing http://standards-oui.ieee.org/oui/oui.csv
       -t, --timestamp      print timestamp
       -T, --deltat sec     tolerance in timestamp comparison
                            (default: 2.5 sec.)
       -O, --ouifile file   IEEE.org host
                            (default: http://standards-oui.ieee.org/oui/oui.csv)
       -o, --outfile file   arpwatch ethercodes
                            (default: ethercodes.dat)
       -p, --patch spec     patch specfile with updated timestamp
```

Example run
-----------

```
$ fetch-ethercodes.py -v
check http://standards-oui.ieee.org/oui/oui.csv
oui file size: 2264884
oui file date: Wed, 26 Sep 2018 08:06:13 GMT
no local file oui.csv found
fetch http://standards-oui.ieee.org/oui/oui.csv
no local file ethercodes.dat found
parse oui.csv
value 0:1:c8 exists already: "THOMAS CONRAD CORP.", "CONRAD CORP."
value 8:0:30 exists already: "NETWORK RESEARCH CORPORATION", "ROYAL MELBOURNE INST OF TECH"
value 8:0:30 exists already: "NETWORK RESEARCH CORPORATION", "CERN"
generate ethercodes.dat with 25433 entries
successful
timestamp: 20180926_080613
```

An additional tool `query-ethercodes.py` is provided, that allows to query the 
ethercodes.dat database.
