from threads import thread_with_exception
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
        self.retry_delay = 10
        self.scan_number_of_retries = 3
        self.plug_status = ""
        self.plug_desired_status = "undetermined"
        self.state_changing_thread = ""
        self.state_checking_thread = ""

    def set_n_of_retries(self, number):
        self.number_of_retries = number

    def set_retry_delay(self, number):
        self.retry_delay = number

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
        for i in range(1, retries + 1):
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
            print("Could not find " + str(self.macAddress) + " - Returning False.")
            return False
        plugReturn = connecter(str(target_ip), self.email, self.password, self.number_of_retries)
        if plugReturn == False:
            return self.initializeConnection()
        self.plug = plugReturn[0]
        self.plug_status = plugReturn[1]
        if self.plug_desired_status != plugReturn[1] and self.plug_desired_status != "undetermined":
            #Plug's desired status does not match it's current status. Reinitiate the changing process.
            if plugReturn[1] == True:
                self.turnOff()
            else:
                self.turnOn()
        return True
    def refreshPlugStatus(self):
        for i in range(1, self.number_of_retries + 1):
            try:
                fetched = self.plug.getDeviceInfo()
                print("Device status refreshed successfully")
                self.plug_status = fetched['result']['device_on']
                if self.plug_status != self.plug_desired_status:
                    if self.plug_desired_status:
                        self.turnOn()
                    else:
                        self.turnOff()
                break
            except:
                print("Checking device status failed. Try " + str(i) + "/" + str(self.number_of_retries))
                if self.retry_delay != -1:
                    time.sleep(self.retry_delay)

    def turnOn(self):
        if self.plug == "not connected":
            return
        self.plug_desired_status = True
        try:
            if self.state_changing_thread.is_alive():
                self.state_changing_thread.raise_exception()
        except (Exception,):
            pass
        self.state_changing_thread = thread_with_exception(self.retry_delay, self.number_of_retries, self.turnOnHandler, {self.plug}, self.initializeConnection, {})
        self.state_changing_thread.start()

    def turnOff(self):
        if self.plug == "not connected":
            return
        self.plug_desired_status = False
        try:
            if self.state_changing_thread.is_alive():
                self.state_changing_thread.raise_exception()
        except (Exception,):
            pass
        self.state_changing_thread = thread_with_exception(self.retry_delay, self.number_of_retries, self.turnOffHandler, {self.plug}, self.initializeConnection, {})
        self.state_changing_thread.start()


    def turnOnHandler(self, plug):
        try:
            plug.turnOn()
            self.plug_status = True
            return "success"
        except (Exception,) as e:
            return False


    def turnOffHandler(self, plug):
        try:
            plug.turnOff()
            self.plug_status = False
            return "success"
        except (Exception,) as e:
            return False


def connecter(target_ip, email, password, retry_amount):
    plug = PyP100.P100(target_ip, str(email), str(password))
    step = 0
    for i in range(1, retry_amount + 1):
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

    for i in range(1, retry_amount + 1):
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
    for i in range(1, retry_amount + 1):
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
