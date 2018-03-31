#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import requests
import shutil
import os
import sys

url_server = "http://api.macvendors.com/"
url_oui = "http://standards-oui.ieee.org/oui/oui.txt"
db_file = os.path.dirname(os.path.abspath(__file__)) + "/oui.txt"

'''
Usage:
    this [-v] [-x] mac_addr
    this [-v] -z mac_addr
    this [-v] update

update: update the local database of OUI. other options are ignored.
'''

s_desc = """
It finds a company name by the mac address specified. if you specify 'update' as
the mac_addr, it is going to update the OUI database taken from the IEEE server.
"""

def parse_args():
    p = argparse.ArgumentParser(description=s_desc)
    p.add_argument("_rest_args", metavar="MAC_ADDR or update", nargs="+",
                   help="MAC address or update.")
    p.add_argument("-z", action="store_true", dest="f_online",
                    help="specify online mode. it's going to ask %s." %
                    url_server)
    p.add_argument("-x", action="store_true", dest="f_reverse",
                    help="specify reverse lookup. the -z option is ignored.")
    p.add_argument("-v", action="store_true", dest="f_verbose",
                   default=False, help="enable verbose mode.")
    args = p.parse_args()
    args.mac_addr = " ".join(args._rest_args)
    return args

'''
test code
'''
opt = parse_args()

if opt.mac_addr == "update":
    if os.path.exists(db_file):
        shutil.move(db_file, db_file + ".bak")
    r = requests.get(url_oui, stream=True)
    if r.status_code == 200:
        with open(db_file, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
                # progress bar
                sys.stdout.write(".")
                sys.stdout.flush()
    print("")
    exit(0)

ma = opt.mac_addr.replace(".","").replace(":","").replace("-","")
ma = ma.replace(" ","")
if len(ma) not in [6, 8, 10, 12]:
    raise ValueError("the length of the MAC address must be either 6, 8, 10, 12")
ma = ("-".join(["%s%s"%(ma[i],ma[i+1]) for i in range(0,6,2)])).upper()
if sys.version_info.major < 3:
    ma = ma.encode(encoding="utf-8")    # for python2

if opt.f_online == True:
    url = url_server + ma
    print(ma)
    res = requests.get(url)
    if res.status_code == 200:
        print(res.text)
    else:
        print("not found")
    exit(0)

with open(db_file, "r") as f:
    for line in f:
        if ma == line[:8]:
            print(line, end="")
