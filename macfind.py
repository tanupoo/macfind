#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import requests
import shutil
import os
import sys

url_server = "http://api.macvendors.com/"
url_oui = "http://standards-oui.ieee.org/oui/oui.txt"
db_file = os.path.dirname(os.path.abspath(__file__)) + "/oui.txt"

def parse_args():
    s_desc = """\
    It finds a company name by the mac address specified.
    
    If you specify 'update', it is going to update the OUI database taken
    from the IEEE server.  It takes a few minutes.

    Usage example:
        macfind (mac_addr)
        macfind -z (mac_addr)
        macfind update\
    """

    p = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=s_desc)
    p.add_argument("_rest_args", metavar="STRING", nargs="+",
                   help="MAC address or update.")
    p.add_argument("-z", action="store_true", dest="f_online",
                    help="specify online mode. it's going to ask %s." %
                    url_server)
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
# only full IPv6 address is supported.
if len(ma) == 32:
    # looks an IPv6 address. takes the host address.
    ma = ma[16:]
if len(ma) == 16:
    # looks the host address of the IPv6 address.
    # inverts the universal bit.
    ma = "{:02x}".format(int(ma[:2], 16)^0x02) + ma[2:6] + ma[10:]
if len(ma) not in [6, 8, 10, 12]:
    raise ValueError("the length of the MAC address must be either 6, 8, 10, 12")
ma = ("-".join(["%s%s"%(ma[i],ma[i+1]) for i in range(0,6,2)])).upper()
if sys.version_info.major < 3:
    ma = ma.encode(encoding="utf-8")    # for python2

print("Searching for", ma)

if opt.f_online == True:
    url = url_server + ma
    res = requests.get(url)
    if res.status_code == 200:
        print(res.text)
    else:
        print("not found")
    exit(0)

with open(db_file, "r") as f:
    count = 0
    for line in f:
        if ma == line[:8]:
            print(line, end="")
            count += 1
    if not count:
        print("not found")
