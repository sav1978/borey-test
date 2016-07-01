#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko
import json
from Tkinter import *

hostname = '10.1.30.42'
username = 'root'
password = 'WGdeaGEnGS3xJADu'  # fix SSH-password if needed
port = 22

def getParkingStatus(event):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostname, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('cat /dsk.var/lua_storage/parking_counter')
    parkingJSON = stdout.read() + stderr.read()
    client.close()
    params = json.loads(parkingJSON)
    totalPlaces.delete(0, END)
    totalPlaces.insert(0, str(params['total']))
    currentCars.delete(0, END)
    currentCars.insert(0, str(params['counter']))

mainWindow = Tk()
mainWindow.geometry('{}x{}'.format(300, 100))
mainWindow.title('Информация о парковке')
Label(mainWindow, text="Всего мест:").place(x=10, y=10)
totalPlaces = Entry(mainWindow, takefocus="no")
totalPlaces.place(x=150, y=10)
Label(mainWindow, text="Машин на стоянке:").place(x=10, y=40)
currentCars = Entry(mainWindow)
currentCars.place(x=150, y=40)
getStatusButton = Button(mainWindow, text = "Обновить информацию")
getStatusButton.bind('<Button-1>', getParkingStatus)
getStatusButton.pack(side='bottom')
mainWindow.mainloop()
