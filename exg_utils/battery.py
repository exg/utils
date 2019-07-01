#!/usr/bin/env python3

import argparse
import xml.etree.ElementTree as ET
import platform
from subprocess import Popen, PIPE
from . import util


def get_battery_info():
    if platform.system() == "Darwin":
        cmd = ["ioreg", "-a", "-c", "AppleSmartBattery"]
        with Popen(cmd, stdout=PIPE) as p:
            tree = ET.parse(p.stdout)
        cur_cap = util.xml_dict_get(tree, "CurrentCapacity")
        max_cap = util.xml_dict_get(tree, "MaxCapacity")
    else:
        with open("/sys/class/power_supply/BAT0/energy_now") as f:
            cur_cap = f.read()
        with open("/sys/class/power_supply/BAT0/energy_full") as f:
            max_cap = f.read()
    return int(cur_cap), int(max_cap)


def main():
    """
    Show the battery status.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "-r", dest="raw", action="store_true", help="show raw values"
    )
    args = parser.parse_args()

    cur_cap, max_cap = get_battery_info()
    if args.raw:
        print("%s/%s" % (cur_cap, max_cap))
    else:
        if max_cap:
            cur_cap = cur_cap / max_cap * 100
        print("%.0f%%" % cur_cap)


if __name__ == "__main__":
    main()
