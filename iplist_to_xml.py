#!/usr/bin/python

from lxml import etree as et

tree = et.parse('boreys.xml')
root = tree.getroot()
f = open("iplist.txt", "r")
for ip in f:
    borey = et.Element("Borey", {"configured":"0"})
    borey.attrib["ipAddress"] = ip.rstrip('\n')
    root.append(borey)
f.close()
f = open("boreys.xml", "w")
f.write(et.tostring(tree, pretty_print=True, xml_declaration=True, encoding='utf-8'))
f.close()
