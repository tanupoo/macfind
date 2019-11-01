#!/usr/bin/env python

import argparse
import requests
import shutil
import os
import sys

url_server = "http://api.macvendors.com/"
url_oui = "http://standards-oui.ieee.org/oui/oui.txt"
db_file = os.path.dirname(os.path.abspath(__file__)) + "/oui.txt"

def pick_oui_name(line):
    """
    return a string of the OUI name.
    line is assumed like
        >>> '00-25-36   (hex)\t\tOki Electric Industry Co., Ltd.\n'
    """
    return " ".join(line.split()[2:])

def macfind_online(oui):
    url = url_server + oui
    res = requests.get(url)
    if res.status_code == 200:
        return pick_oui_name(res.text)
    else:
        return ""

def macfind_offline(oui):
    with open(db_file, "r") as f:
        for line in f:
            if oui == line[:8]:
                return pick_oui_name(line)
    return ""

def macfind(ma, online=False, enable_ipv6=False):
    oui = get_canonical_macaddr(ma, enable_ipv6)
    if online is True:
        return macfind_online(oui)
    else:
        return macfind_offline(oui)

def get_canonical_macaddr(mac_addr, enable_ipv6=False):
    """
    return the OUI of xx-xx-xx style.
    """
    ma = mac_addr.replace(".","").replace(":","").replace("-","")
    ma = ma.replace(" ","")
    if enable_ipv6:
        # only full IPv6 address is supported.
        if len(ma) == 32:
            # looks an IPv6 address. takes the host address.
            ma = ma[16:]
        if len(ma) == 16:
            # looks the host address of the IPv6 address.
            # inverts the universal bit.
            ma = "{:02x}".format(int(ma[:2], 16)^0x02) + ma[2:6] + ma[10:]
    else:
        # the length of 16 should be acceptable.
        if len(ma) not in [6, 8, 10, 16, 12]:
            raise ValueError("the length of the MAC address must be either 6, 8, 10, 12")
        ma = ("-".join(["%s%s"%(ma[i],ma[i+1]) for i in range(0,6,2)])).upper()
    if sys.version_info.major < 3:
        return ma.encode(encoding="utf-8")    # for python2
    else:
        return ma

"""
test code
"""
if __name__ == "__main__":
    s_desc = """\
    It finds a company name by the mac address specified.
    
    If you specify 'update', it is going to update the OUI database taken
    from the IEEE server.  It takes a few minutes.

    Usage example:
        macfind (mac_addr)
        macfind -z (mac_addr)
        macfind update\
    """

    ap = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=s_desc)
    ap.add_argument("_rest_args", metavar="STRING", nargs="+",
                   help="MAC address or update.")
    ap.add_argument("-6", action="store_true", dest="enable_ipv6",
                    help="specify the argument is an IPv6 address.")
    ap.add_argument("-z", action="store_true", dest="f_online",
                    help="specify online mode. it's going to ask %s.".format(
                            url_server))
    opt = ap.parse_args()
    opt.mac_addr = " ".join(opt._rest_args)

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

    print("Searching for", opt.mac_addr)

    ret = macfind(opt.mac_addr, online=opt.f_online)
    if ret:
        print(ret)
    else:
        print("Not found")
