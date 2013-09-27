'''
Created on 18/09/2013

@author: david
'''
from ConfigObject import ConfigObject
import ast
from threading import Thread
import threading
import time
import usb


DEVICE_NAME = 'name'
DEVICE_VENDORID = 'vendorid'
DEVICE_PRODUCTID = 'productid'
DEVICE_MANUFACTURER = 'manufacturer'

class Action(object):
    ADD, REMOVE = range(0,2)

class FindUSB(threading.Thread):
    def __init__(self, update):
        Thread.__init__(self)
        self.CONFIG_FILENAME = 'devices.ini'
        self.configuration = ConfigObject(filename=self.CONFIG_FILENAME)
        devicesNames = dict(self.configuration.devices)
        self.deviceItems = (devicesNames.items())
        self.devicesActives = {}
        self.update = update        
    
    def _filter(self,dev):
        if dev.bDeviceClass == usb.legacy.CLASS_COMM: 
            return True
        elif dev.bDeviceClass == usb.legacy.CLASS_PER_INTERFACE:
            device = usb.legacy.Device(dev)
            for interface in device.configurations[0].interfaces[0]:
                if interface.interfaceClass == usb.legacy.CLASS_COMM or interface.interfaceClass == usb.legacy.CLASS_VENDOR_SPEC:
                    return True
    
    def _compareData(self, dev):
        oldDevicesActives = list(self.devicesActives.values())
        
        newData = dict(zip([x.idVendor for x in dev],[x.idProduct for x in dev]))
        oldData = dict(zip([x.idVendor for x in oldDevicesActives],[x.idProduct for x in oldDevicesActives]))
        
        # Find the connections lost
        intersectOldToNew = set(oldData.items()) - set(newData.items())
        
        # Find the new Devices found not registered  
        intersectNewToOld = dict(set(newData.items()) - set(oldData.items()))        
        
        if intersectOldToNew != set():
            self._removeDevice(intersectOldToNew)                    
        
        #print("OLD to NEW = "+str(intersectOldToNew))
        #print("NEW to OLD = "+str(intersectNewToOld))
        
        return intersectNewToOld
    
    def _removeDevice(self, intersectOldToNew):
        dataToRemove = dict(intersectOldToNew)

        for key in self.devicesActives.keys():
            device = self.devicesActives[key]
            if device.idVendor in dataToRemove.keys():
                if device.idProduct == dataToRemove[device.idVendor]:
                    print("Removing "+key)
                    self.update(Action.REMOVE, key)                     
                    del self.devicesActives[key]
                    
                    return
                
    def _clearDeviceList(self):
        for key in self.devicesActives:
            self.update(Action.REMOVE, key)
        self.devicesActives.clear()
                    
    def run(self):
        while(True):
            dev = []
            devicesToUpdate = {}      
            try:
                dev = usb.core.find(find_all=True, custom_match = self._filter)
            except:
                dev = []
            if (dev!=[]):
                newDevices = self._compareData(dev)            
                if (newDevices!={}):                    
                    for d in dev:
                        #try:
                            if newDevices[d.idVendor]==d.idProduct:
                                device = usb.legacy.Device(d)            
                                #print("DADOS:")            
                                #print('Hexadecimal VendorID=' + hex(device.idVendor) + ' & ProductID=' + hex(device.idProduct))
                                
                                for items in self.deviceItems:
                                    #print("* "+items[0])
                                    deviceData = ast.literal_eval(items[1])
                                    #print("vendor id  "+ deviceData[DEVICE_VENDORID] +" - "+ str(hex(device.idVendor)))
                                    #print("product id "+ deviceData[DEVICE_PRODUCTID] +" - "+ str(hex(device.idProduct)))
                                    if deviceData[DEVICE_VENDORID] == str(hex(device.idVendor)) and deviceData[DEVICE_PRODUCTID] == str(hex(device.idProduct)):
                                        if items[0] not in self.devicesActives.keys():
                                            print("insert "+str(deviceData[DEVICE_NAME]))                            
                                            self.devicesActives[items[0]] = d
                                            devicesToUpdate[items[0]] = d
                                    
                                if devicesToUpdate != {}:
                                    self.update(Action.ADD, devicesToUpdate)
                        #except Exception as ex:
                            #print("Exception: "+format(ex))
            elif self.devicesActives != {}: 
                self._clearDeviceList() 
                          
            time.sleep(3)
                
if __name__ == '__main__':
    seila = {}
    usbData = FindUSB(seila)
    usbData.start()
    
    def atualiza(self, isremove, data):
        print("action -> "+isremove)
        if isremove:
            print("removing "+data)
            
        else: 
            for key in data.keys():
                print("Adding "+key)                