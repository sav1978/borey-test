#!/usr/bin/python
from lxml import etree as et
import os

tree = et.parse("boreys.xml")

boreys = tree.xpath("/Boreys/Borey[@changecard='1']")

for borey in boreys:
    raw_input("\nPress ENTER to continue!")
    default_ip = borey.get("ipAddress")
    default_mac = borey.get("macAddress")
    os.system("bash ./ultima-ext-packager.sh /dev/mmcblk0 {} {}".format(default_ip, default_mac))
    borey.attrib["activated"] = "1"
    f = open("boreys.xml", "w")
    f.write(et.tostring(tree, pretty_print=True, xml_declaration=True, encoding='utf-8'))
    f.close()