#!/usr/bin/python

from lxml import etree as et

filename = 'iplist.txt'
xml_filename = 'boreys.xml'

root = et.Element('Boreys')
f = open(filename, "r")
for ip in f:
    borey = et.Element("Borey", {"configured":"0"})
    borey.attrib["ipAddress"] = ip.rstrip('\n')
    root.append(borey)
f.close()
f = open(xml_filename, "w")
f.write(et.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'))
f.close()