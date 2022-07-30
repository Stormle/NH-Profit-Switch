from threads import RepeatTimer
import nmap
import os
from PyP100 import PyP100, PyP110
import time


class MinerPlug:
    def __init__(self, macAddress, ipMask, email, password):
        self.plug = "not connected"
        self.email = email
        self.password = password
        self.macAddress = macAddress
        self.ipMask = ipMask
        self.number_of_retries = 10
        self.scan_number_of_retries = 3
        self.plug_status = ""
        self.plug_desired_status = ""

    def set_n_of_retries(self, number):
        self.number_of_retries = number

    def set_scan_n_of_retries(self, number):
        self.scan_number_of_retries = number

    def initializeConnection(self):
        retries = self.scan_number_of_retries
        target_mac = self.macAddress
        nm = ""
        if os.name == 'nt':
            nmap_path = [r"C:\Program Files (x86)\Nmap\nmap.exe", ]
            nm = nmap.PortScanner(nmap_search_path=nmap_path)
        else:
            nm = nmap.PortScanner()
        print("Scanning local network for MAC " + str(self.macAddress))
        target_ip = "not found"
        for i in range(1, retries):
            if target_ip != "not found":
                break
            nm.scan(hosts=self.ipMask, arguments='-F')
            host_list = nm.all_hosts()
            for host in host_list:
                if 'mac' in nm[host]['addresses']:
                    if target_mac == nm[host]['addresses']['mac']:
                        print("Device IP found: " + str(nm[host]['addresses']['ipv4']))
                        target_ip = nm[host]['addresses']['ipv4']
                        break
            if target_ip == "not found":
                print("MAC " + str(self.macAddress) + " not found. Try " + str(i) + "/" + str(retries))

        if target_ip == "not found":
            print("Could not find" + str(self.macAddress) + "Returning False.")
            return False
        plugReturn = connecter(str(target_ip), self.email, self.password, self.number_of_retries)
        self.plug = plugReturn[0]
        self.plug_status, self.plug_desired_status = plugReturn[1]
        return True

    def turnOn(self):
        if self.plug == "not connected":
            return
        self.plug_desired_status = True
        timer = RepeatTimer(5, tryOn(self))

def tryOn(self, max_tries):
    try:
        self.plug.turnOn()
    except:
        print()

def connecter(target_ip, email, password, retry_amount):
    plug = PyP100.P100(target_ip, str(email), str(password))
    step = 0
    for i in range(1, retry_amount):
        try:
            plug.handshake()
            print(str(target_ip) + " handshake success")
            step += 1
            break
        except:
            print(str(target_ip) + " handshake " + str(i) + "/" + str(retry_amount) + " failed")
            time.sleep(5)

    if step == 0:
        return False

    for i in range(1, retry_amount):
        try:
            plug.login()
            print(str(target_ip) + " login success")
            step += 1
            break
        except:
            print(str(target_ip) + " login " + str(i) + "/" + str(retry_amount) + " failed")
            time.sleep(5)

    if step < 2:
        return False
    deviceStatus = False
    for i in range(1, retry_amount):
        try:
            fetched = plug.getDeviceInfo()
            deviceStatus = fetched['result']['device_on']
            print(str(target_ip) + " fetching device status succeeded")
            step += 1
            break
        except:
            print(str(target_ip) + " device status fetching " + str(i) + "/" + str(retry_amount) + " failed")
            time.sleep(5)
    if step == 3:
        return plug, deviceStatus
    else:
        return False
