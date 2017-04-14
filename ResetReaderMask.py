#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko
from lxml import etree as et

username = 'root'
password = 'hcKGB9PY6GQluPra'  # fix SSH-password if needed


def reset_reader_mask(host, user, sshpass, port=22):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=sshpass, port=port)
    stdin, stdout, stderr = client.exec_command('ls /dsk/var/pacs | grep .conf')
    filesList = stdout.read() + stderr.read()
    files = filesList.split()
    for ap_config in files:
        if not ap_config.startswith("pacs"):
            stdin, stdout, stderr = client.exec_command('cat /dsk/var/pacs/' + ap_config)
            f = stdout.read() + stderr.read()
            f = f.split('\n')
            client.exec_command('rm /dsk/var/pacs/' + ap_config)
            for line in f:
                if line.startswith('other.card_mask'):
                    cmd = 'echo -e "other.card_mask=FFFFFFFFFFFFFFFF" >> /dsk/var/pacs/' + ap_config
                else:
                    cmd = 'echo -e "' + line + '" >> /dsk/var/pacs/' + ap_config
                stdin, stdout, stderr = client.exec_command(cmd)
                while not stdout.channel.exit_status_ready():
                    pass
    client.exec_command('pkill appsrv')
    client.close()

tree = et.parse("boreys.xml")

boreys = tree.xpath("/Boreys/Borey[@maskResetted='0']")

for borey in boreys:
    raw_input("\nPress ENTER to continue!")
    ip = borey.get("ipAddress")
    print 'Resetting readers mask of Borey with ip {}'.format(ip)
    reset_reader_mask(ip, username, password)
    borey.attrib["maskResetted"] = "1"
    f = open("boreys.xml", "w")
    f.write(et.tostring(tree, pretty_print=True, xml_declaration=True, encoding='utf-8'))
    f.close()
