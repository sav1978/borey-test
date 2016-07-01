# -*- coding: utf-8 -*-
import os, time,  sys, pyping
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import socket
from lxml import etree
import logging
import winsound

#from socket import socket, gethostbyname, AF_INET, SOCK_STREAM
#from socket import AF_INET, SOCK_STREAM
FILE_XML='test.xml'
RE_COMP=0
#DELEY_GO_BR=0.4
CAM_NETWORK_DEFINE = ['192.0.0.5','255.255.255.0','192.0.0.1']
CAM_NETWORK_MANN=['10.100.16.5','255.255.255.0','10.100.16.1']
IP_FROM_CAM_DEFINE='192.0.0.64'
#IP_FROM_CAM_DEFINE='192.168.88.15'
SET_CAM_NAME='DEV_001'
SET_CAM_NAMBER='01'
SET_CAM_TIME_SERVER='192.168.88.10'
SET_CAM_TIME_INTERVAL='240'
SET_CAM_DNS_ADDRESS='192.168.88.1'
MODEL_CAM_CONFIG=""
SET_CAM_NETWORK=['192.168.88.16','255.255.255.0','192.168.88.1']
NUMBER_WEB_SET=6

logging.basicConfig(filename='script_work.log', level=logging.INFO)



##################################################################################################################
def set_ip(host_ip):
    print ""
    print ""
    sys.stdout.write("SET IP STATIC ADRESS  :"+host_ip[0]+"     ")
    logging.info( "SET IP ADRESS  :"+host_ip[0])
    get_ip=socket.gethostbyname(socket.gethostname())
    if get_ip!=host_ip[0]:
        os.system('netsh interface ipv4 set address name="Ethernet" source=static address='+host_ip[0]+' mask='+host_ip[1]+' gateway='+host_ip[2])
        i=0        
        while get_ip != host_ip[0] :
            ip_t=socket.gethostbyname(socket.gethostname())
            if ip_t!='127.0.0.1':
                get_ip=ip_t
            
            if i==0:
                sys.stdout.write("Processing ") 
            else:
                sys.stdout.write(".")
            time.sleep(1)
            if i < 60: 
                i = i + 1
            else:
                sys.stdout.write( "    WAIT "+str(i)+" SEC STOPPED, IP ADDRESS :"+get_ip)
                break      
        sys.stdout.write("OK, SET STATIC IP ADRESS HOST :"+get_ip)
        logging.info("OK, SET STATIC IP ADRESS HOST :"+get_ip)
    else:
        sys.stdout.write("IP :"+str(host_ip)+" established")
        logging.error("IP :"+str(host_ip)+" established")

def set_ip_dhcp():
    print "SET IP ADRESS  : DHCP"
    logging.info( "SET IP ADRESS  : DHCP")
    host_ip=socket.gethostbyname(socket.gethostname())
    get_ip=host_ip
    os.system('netsh interface ipv4 set address name="Ethernet" source=dhcp')
    i=0        
    while get_ip == host_ip :
        ip_t=socket.gethostbyname(socket.gethostname())
        if ip_t!='127.0.0.1':
            get_ip=ip_t
        if i==0:
            sys.stdout.write("Processing ") 
        else:
            sys.stdout.write(".")
        time.sleep(1)
        if i < 60: 
            i = i + 1
        else:
            print "WAIT ",i," SEC, STOPPED, IP ADDRESS :",get_ip
            logging.error( "WAIT "+i+" SEC, STOPPED, IP ADDRESS :",get_ip)
            break
    print ""   
    print "OK, IP ADRESS HOST FROM DHCP :",get_ip
    logging.info("OK, IP ADRESS HOST FROM DHCP :"+get_ip)
    
def ping_ip_address(time_aut_ping,ip_address_ping): 
    print ""
    sys.stdout.write("START PING IP ADDRESS:"+ip_address_ping+"   ")    
    i=0
    ping_ok=1
    while ping_ok==1:
        ping_ip=pyping.ping(ip_address_ping,count=2)
        ping_ok=ping_ip.ret_code
        if i < time_aut_ping:
            if i==0:
                sys.stdout.write("ping ") 
            else:
                sys.stdout.write(".") 
            i=i+1 
        else:
            sys.stdout.write("WAIT "+str(i)+", PING IP ADDRESS STOP :")
            break                      
    if ping_ok==0:
        sys.stdout.write("      IP ADRESS:"+ip_address_ping+" AVALIBLE")
        return 1            
    else:
        sys.stdout.write("      IP ADRESS:"+ip_address_ping+" IS'T AVALIBLE")              
        return  0

def get_port(targetIP,port):
    from socket import socket, gethostbyname, AF_INET, SOCK_STREAM
    s = socket(AF_INET, SOCK_STREAM)
    result = s.connect_ex((targetIP, port))
    if(result == 0) :
        return 0
    else:
        return 1
    s.close()
       
def open_ip_port(time_aut_ping,ip_address_ping): 
    print ""
    sys.stdout.write("START OPEN PORT 80 FROM:"+ip_address_ping+"   ")    
    i=0
    ping_ok=1
    while ping_ok==1:
        ping_ok=get_port(ip_address_ping,80)
        if i < time_aut_ping:
            if i==0:
                sys.stdout.write("open port ") 
            else:
                sys.stdout.write(".") 
            i=i+1 
        else:
            sys.stdout.write("WAIT "+str(i)+", OPEN PORT STOP")
            break                      
    if ping_ok==0:
        sys.stdout.write("     PORT 80 IN HOST:"+ip_address_ping+" IS OPEN")
        return 1            
    else:
        print ""
        sys.stdout.write("     PORT 80 IN HOST:"+ip_address_ping+" IS CLOSED")       
        return  0

##################################################################################################################

def get_setings_of_model(model_cam):
    global SET_CAM_NAMBER, SET_CAM_NAME, SET_CAM_TIME_SERVER, SET_CAM_NETWORK, SET_CAM_DNS_ADDRESS ,MODEL_CAM_CONFIG
    MODEL_CAM_CONFIG=model_cam
    root = etree.parse(FILE_XML)
    nodes = root.xpath('/IP_HIKVISION/'+model_cam+'/CAM') 
    err_get_conf=1
    for node in nodes:
        if node.get('set_config') == '0':
            err_get_conf=0
            SET_CAM_NAMBER=node.get('id').encode('utf-8')
            SET_CAM_NAME=node.get('name').encode('utf-8') 
            SET_CAM_TIME_SERVER=node.get('ntp_server').encode('utf-8')
            SET_CAM_NETWORK=[node.get('ip').encode('utf-8'),node.get('netmask').encode('utf-8'),node.get('gateway').encode('utf-8')]
            SET_CAM_DNS_ADDRESS=node.get('dns_server').encode('utf-8')
            break
    return err_get_conf

def get_all():
    #global SET_CAM_NAMBER, SET_CAM_NAME, SET_CAM_TIME_SERVER, SET_CAM_NETWORK, SET_CAM_DNS_ADDRESS ,MODEL_CAM_CONFIG
    #MODEL_CAM_CONFIG=model_cam
    global FILE_XML
    root = etree.parse(FILE_XML)

    nodes = root.xpath("//CAM")
    all_cam=0
    for node in nodes:
        if node.get('set_config') == '0':
            all_cam=all_cam+1
    print "CONFIG CAM SET: ",all_cam


def save_setings_of_model():
    root = etree.parse(FILE_XML)
    nodes = root.xpath('/IP_HIKVISION/'+MODEL_CAM_CONFIG+'/CAM') 
    err_get_conf=1
    for node in nodes:
        if node.get('name').encode('utf-8') == SET_CAM_NAME:
            err_get_conf=0
            node.attrib['set_config'] = "1"
            break
    root.write(FILE_XML, pretty_print=True, xml_declaration=True)
    return err_get_conf


##################################################################################################################
def frame_available_cb(frame_reference):
    from selenium.common.exceptions import NoSuchFrameException
    """Return a callback that checks whether the frame is available."""
    def callback(browser):
        try:
            browser.switch_to_frame(frame_reference)
        except NoSuchFrameException:
            return False
        else:
            return True
    return callback


def woit_id_html(driver,html_id):
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, html_id)))
    finally:
        logging.info("wait id "+html_id+" : OK!")

def push_enter_of_classname(driver,html_classname):
    push_enter=driver.find_element_by_class_name(html_classname)
    push_enter.send_keys(Keys.ENTER)

def push_enter_of_id(driver,html_id):
    push_enter=driver.find_element_by_id(html_id)
    push_enter.send_keys(Keys.ENTER)

def set_text_of_id(driver,html_id,set_html_value):
    hik_conf=driver.find_element_by_id(html_id);  
    hik_conf.clear()
    hik_conf.send_keys(set_html_value)
    
def comp_text_of_id(driver,html_id,set_html_value):
    hik_conf=driver.find_element_by_id(html_id);
    if hik_conf.get_attribute('value').encode('utf-8') == set_html_value:
        return 0
    else:
        return 1
    
    
def set_value_and_comp_of_id(driver,html_id,set_html_value):    
    global err_conf
    woit_id_html(driver,html_id)
    i=0
    set_ok=1
    while set_ok==1:
        set_text_of_id(driver,html_id,set_html_value)
        set_ok=comp_text_of_id(driver,html_id,set_html_value)
        if i < NUMBER_WEB_SET:
            i=i+1 
        else:
            sys.stdout.write("WAIT "+str(i)+", set "+set_html_value+" in "+html_id+" : err!")
            break                      
    if comp_text_of_id(driver,html_id,set_html_value)==0:
        logging.info("set "+set_html_value+" in "+html_id+" : OK!")
        return 1            
    else:
        err_conf=err_conf+1
        logging.error("set "+set_html_value+" in "+html_id+" : err!")
        return  0

def comp_value_if_id(driver,html_id,set_html_value):    
    global err_comp, RE_COMP
    
    woit_id_html(driver,html_id)
    i=0
    set_ok=1
    while set_ok==1:
        set_ok=comp_text_of_id(driver,html_id,set_html_value)
        if i < NUMBER_WEB_SET:
            i=i+1 
        else:
            sys.stdout.write("WAIT "+str(i)+", comp_and_set "+set_html_value+" in "+html_id+" : err!")
            break                      
    if comp_text_of_id(driver,html_id,set_html_value)==0:
        logging.info("comp "+set_html_value+" in "+html_id+" : OK!")
        return 1            
    else:
        err_comp=err_comp+1
        logging.error("comp "+set_html_value+" in "+html_id+" : err!")
        return  0

def conf_web(ip_cam_config):
    global err_conf
    err_conf=0

    driver = webdriver.Firefox()
    driver.set_page_load_timeout(20)
    mouse = webdriver.ActionChains(driver)
    driver.get("http://"+ip_cam_config)
    
    set_value_and_comp_of_id(driver,"UserName","admin")
    set_value_and_comp_of_id(driver,"Password","12345")
    push_enter_of_classname(driver,"mousepointer")

    woit_id_html(driver,"devicetype")
    hik_conf=driver.find_element_by_id("devicetype");  
    cam_m=get_setings_of_model(hik_conf.text.encode('utf-8'))
    #cam_m=0
    if  cam_m==0: 
        print " " 
        print " "
        print " " 
        sys.stdout.write("SETUP CAM  ID : "+SET_CAM_NAMBER+" NAME : "+SET_CAM_NAME+" IP : "+SET_CAM_NETWORK[0])
        logging.info("SETUP CAM  ID : "+str(SET_CAM_NAMBER)+" NAME : "+SET_CAM_NAME+" IP : "+SET_CAM_NETWORK[0])
        print " "
        print " "
        print " "
                
        hik_but= driver.find_element_by_id("iMenu4")
        mouse.move_to_element(hik_but).click().perform()
        try:
           element =  WebDriverWait(driver, timeout=10).until(frame_available_cb("contentframe"))
        finally:
            logging.info("Go to frame : OK!")
        #hik_conf=driver.switch_to_frame("contentframe")
        
        if set_value_and_comp_of_id(driver,'teDeviceName',SET_CAM_NAME):
            push_enter_of_classname(driver,"savebtn")

        if set_value_and_comp_of_id(driver,'teDeviceID',SET_CAM_NAMBER):
            push_enter_of_classname(driver,"savebtn")

        woit_id_html(driver,"aTimeSettings")        
        push_enter_of_id(driver,"aTimeSettings")

        woit_id_html(driver,"seTimeZone")
        hik_conf = Select(driver.find_element_by_id('seTimeZone'))
        hik_conf.select_by_value('CST-3:00:00')
        push_enter_of_classname(driver,"savebtn")
        logging.info("set time zone : OK!")
        
        hik_but=driver.find_elements_by_css_selector("input[type='radio']")[0].click()
        
        if set_value_and_comp_of_id(driver,"teNtpServer",SET_CAM_TIME_SERVER):
            push_enter_of_classname(driver,"savebtn")

        if set_value_and_comp_of_id(driver,'teNtpInterval',SET_CAM_TIME_INTERVAL):
            push_enter_of_classname(driver,"savebtn")

        woit_id_html(driver,"aNetwork")       
        push_enter_of_id(driver,"aNetwork")
        woit_id_html(driver,"ipAddress")   
        
        if set_value_and_comp_of_id(driver,"subnetMask",SET_CAM_NETWORK[1]):
            push_enter_of_id(driver,"SaveConfigBtn")

        if set_value_and_comp_of_id(driver,"DefaultGateway",SET_CAM_NETWORK[2]):
            push_enter_of_id(driver,"SaveConfigBtn")

        try:
            WebDriverWait(driver, 4).until(EC.alert_is_present(),
                                           u'Вы хотите перезагрузить устройство??')
        
            alert = driver.switch_to.alert()
            alert.dismiss()
        except TimeoutException:
            sys.stdout.write("..")

        if set_value_and_comp_of_id(driver,"PrimaryDNS",SET_CAM_DNS_ADDRESS):
            push_enter_of_id(driver,"SaveConfigBtn")
        
        if set_value_and_comp_of_id(driver,"ipAddress",SET_CAM_NETWORK[0]):
            push_enter_of_id(driver,"SaveConfigBtn")

        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                           u'Вы хотите перезагрузить устройство??')
        
            alert = driver.switch_to.alert()
            alert.accept()
            sys.stdout.write("..")
        except TimeoutException:
            sys.stdout.write("..")
        if err_conf==0:
            print "  "
            logging.info("set IP settings : OK!")
            sys.stdout.write("set IP settings : OK!")
            driver.close()
        else:
            print "  "
            logging.error("set IP error !")
            sys.stdout.write("set IP error !")   
    else:
        logging.error("ERROR GET SRTINGS FROM XML") 
        sys.stdout.write("ERROR GET SRTINGS FROM XML")
        err_conf=err_conf+1

def comp_web(ip_cam_comp):
    global err_comp, RE_COMP
    err_comp=0
    RE_COMP=0
    driver = webdriver.Firefox()
    driver.set_page_load_timeout(20)
    mouse = webdriver.ActionChains(driver)
    driver.get("http://"+ip_cam_comp)

    set_value_and_comp_of_id(driver,"UserName","admin")
    set_value_and_comp_of_id(driver,"Password","12345")
    push_enter_of_classname(driver,"mousepointer")
    
    woit_id_html(driver,"devicetype")
    hik_but= driver.find_element_by_id("iMenu4")
    mouse.move_to_element(hik_but).click().perform()
        
    try:
         element =  WebDriverWait(driver, timeout=10).until(frame_available_cb("contentframe"))
    finally:
        logging.info("Go to frame : OK!")
    
    
    
    comp_value_if_id(driver,'teDeviceName',SET_CAM_NAME)
    comp_value_if_id(driver,'teDeviceID',SET_CAM_NAMBER)
            
    push_enter_of_id(driver,"aTimeSettings")
    
    comp_value_if_id(driver,'teNtpServer',SET_CAM_TIME_SERVER)

    push_enter_of_id(driver,"aNetwork")
    woit_id_html(driver,"ipAddress")             
    comp_value_if_id(driver,"subnetMask",SET_CAM_NETWORK[1])
    comp_value_if_id(driver,"DefaultGateway",SET_CAM_NETWORK[2])
    comp_value_if_id(driver,"ipAddress",SET_CAM_NETWORK[0])
    driver.close() 
    if err_comp==0:
        logging.info("Comparete IP settings : OK!")
        return 0
    else:
        logging.error("sComparete IP error !")
        print "Comparete IP error !" 
        return 1
       
""""""

def set_parametrs(ip_cam_set):
    if ping_ip_address(600,ip_cam_set):
        if  open_ip_port(60,ip_cam_set):
            winsound.Beep(300,700) 
            print ""
            sys.stdout.write("START CONGIG IP CAMERA")
            conf_web(ip_cam_set)

            if err_comp==0:
                sys.stdout.write("     STOP CONFIG IP CAMERA, OK")
            else:
                sys.stdout.write("     STOP CONFIG IP CAMERA, ERROR")
        else: 
            sys.stdout.write("     ERROR OPEN PORT CONFIG IP CAMERA")                
    else:
        sys.stdout.write("     ERROR PING IP CONFIG CAMERA")
            
def comp_parametrs(ip_cam_comp):
    global err_comp, RE_COMP
    err_comp=1
    i=0    
    if ping_ip_address(60,ip_cam_comp):
        if  open_ip_port(60,ip_cam_comp):
            #winsound.Beep(300,200) 
            print ""
            sys.stdout.write("START COMPARED IP CAMERA")
            #time.sleep(3)
            #RE_COMP=0
            while err_comp>0:   
                #time.sleep(50)
                if comp_web(ip_cam_comp):
                    conf_web(ip_cam_comp)
                if i < NUMBER_WEB_SET:
                    i=i+1 
                else:
                    sys.stdout.write("WAIT "+str(i)+", comp_parametrs "+ip_cam_comp+" : err!")
                    break  
            if err_comp==0:
                sys.stdout.write("     STOP COMPARED IP CAMERA, OK")
                save_setings_of_model()
                winsound.Beep(300,300)
                time.sleep(0.3)
                winsound.Beep(300,300)
            else:
                sys.stdout.write("     STOP COMPARED IP CAMERA, ERROR")
                winsound.Beep(300,200)
                winsound.Beep(300,200)          
                winsound.Beep(300,200)
        else: 
            sys.stdout.write("     ERROR OPEN PORT COMPARED IP CAMERA")
    else:

            sys.stdout.write("         ERROR PING IP COMPARED IP CAMERA")
        
err_conf=0
err_comp=0   
while err_comp==0:       
   
    set_ip(CAM_NETWORK_DEFINE)  
    set_parametrs(IP_FROM_CAM_DEFINE)
    get_all()
    set_ip(CAM_NETWORK_MANN)
    comp_parametrs(SET_CAM_NETWORK[0]) 
    #comp_parametrs(IP_FROM_CAM_DEFINE)
    #time.sleep(20)

#set_ip_dhcp()
"""

os.system('netsh interface ipv4 set address name="Ethernet" source=dhcp')
time.sleep(11)
print "get local ip address from DHCP"
Local_ip_dhcp=socket.gethostbyname(socket.gethostname())
print "IP ADRESS FROM DHCP :",Local_ip_dhcp



os.system('netsh interface ipv4 set address name="Ethernet" source=static address=192.168.88.12 mask=255.255.255.0 gateway=192.168.88.1')
print "IP ADRESS CHANGED ON STATOC!"
time.sleep(5) 
ip_address_l = socket.gethostbyname(socket.gethostname())
print ip_address_l
os.system('netsh interface ipv4 set address name="Ethernet" source=dhcp')
print "IP ADRESS CHANGED ON DHCP!"
ip_address_l = socket.gethostbyname(socket.gethostname())
time.sleep(5) 
print ip_address_l
ip_address_l = socket.gethostbyname(socket.gethostname())
time.sleep(5) 
print ip_address_l
ip_address_l = socket.gethostbyname(socket.gethostname())
time.sleep(5) 
print ip_address_l


""" 