#!/usr/bin/env python

import argparse
import requests
import shutil
import os
import sys

url_server = "http://api.macvendors.com/"
oui_db = [
    {
        "id": "ieee",
        "url": "http://standards-oui.ieee.org/oui/oui.txt",
        "name": "oui.txt"
    },
    {
        "id": "wireshark",
        "url": "https://gitlab.com/wireshark/wireshark/-/raw/master/manuf",
        "name": "wsk.txt"
    }
    ]

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

def macfind_offline_ieee(oui):
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           oui_db[0]["name"])
    with open(db_file, "r") as f:
        for line in f:
            if oui == line[:8]:
                return pick_oui_name(line)
    return None

def macfind_offline_wireshark(oui):
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           oui_db[1]["name"])
    oui = oui.replace("-",":")
    with open(db_file, "r") as f:
        for line in f:
            if oui == line[:8]:
                return pick_oui_name(line)
    return None

def macfind_offline(oui):
    r = macfind_offline_ieee(oui)
    if r is not None:
        return r
    r = macfind_offline_wireshark(oui)
    if r is not None:
        return r
    else:
        return ""

def macfind(ma, online=False, enable_ipv6=False):
    oui = get_canonical_macaddr(ma, enable_ipv6)
    x = bin(int(oui[:2],16))[2:].zfill(8)
    if online is True:
        return macfind_online(oui), x[6], x[7]
    else:
        return macfind_offline(oui), x[6], x[7]

def get_canonical_macaddr(mac_addr, enable_ipv6=False):
    """
    return the OUI of XX-XX-XX style.
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

    if opt.mac_addr == "test":
        test_lines = [
            "ac-bc-32-ba-1c-9f",
            "ac.bc.32.ba.1c.9f",
            "acbc.32ba.1c9f",
            "ac:bc:32:ba:1c:9f",
            "ac bc 32 ba 1c 9f",
            "ac bc 32",
            "7b12:e437:9c2c:fa76",
            ]
        for v in test_lines:
            print(v, "=>", macfind(v))
        exit(0)

    if opt.mac_addr == "update":
        nb_count_prog = 1024000
        nb_count = 0
        for url in oui_db:
            db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   url["name"])
            db_url = url["url"]
            try:
                r = requests.get(db_url, stream=True, timeout=(3.0, 6.0))
                if r.status_code == 200:
                    tmp_file = f"{db_file}.tmp"
                    with open(tmp_file, "wb") as f:
                        for chunk in r:
                            f.write(chunk)
                            # progress bar
                            nb_count += len(chunk)
                            if nb_count > nb_count_prog:
                                nb_count = 0
                                sys.stdout.write(".")
                                sys.stdout.flush()
            except Exception as e:
                raise
            else:
                if os.path.exists(db_file):
                    shutil.move(db_file, f"{db_file}.bak")
                shutil.move(tmp_file, db_file)
                print("")
        exit(0)

    print("Searching for", opt.mac_addr)

    ret = macfind(opt.mac_addr, online=opt.f_online)
    if ret[0]:
        print(ret[0])
    else:
        print("Not found.")
        if ret[1] == "1":
            print("Local bit {}.".format(ret[1]))
        if ret[2] == "1":
            print("Group bit {}.".format(ret[2]))
