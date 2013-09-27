'''
Created on 18/09/2013

@author: david
'''
from ConfigObject import ConfigObject
import ast
import dbus
import sys
import time
import usb

import main


DEVICE_NAME = 'name'
DEVICE_VENDORID = 'vendorid'
DEVICE_PRODUCTID = 'productid'
DEVICE_MANUFACTURER = 'manufacturer'

class findUSB(object):
    def __init__(self, observer):
        self.CONFIG_FILENAME = 'devices.ini'
        self.configuration = ConfigObject(filename=self.CONFIG_FILENAME)
        devicesNames = dict(self.configuration.devices)
        self.deviceItems = (devicesNames.items())
        self.devicesActives = {}
        self.observer = observer
    
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
                    del self.devicesActives[key]
                    return
                    
    def run(self):
        while(True):
            dev = []      
            try:
                dev = usb.core.find(find_all=True, custom_match = self._filter)
            except:
                dev = []
            if (dev!=[]):
                hasNewDevices = self._compareData(dev)            
                if (hasNewDevices!={}):
                    for d in dev:
                        try:
                            if hasNewDevices[d.idVendor]==d.idProduct:
                                device = usb.legacy.Device(d)            
                    #print("DADOS:")            
                    #print('Hexadecimal VendorID=' + hex(device.idVendor) + ' & ProductID=' + hex(device.idProduct))
                    
                                for items in self.deviceItems:
                        #print("* "+items[0])
                                    deviceData = ast.literal_eval(items[1])
                                    if deviceData[DEVICE_VENDORID] == str(hex(device.idVendor)) and deviceData[DEVICE_PRODUCTID] == str(hex(device.idProduct)):
                                        if items[0] not in self.devicesActives.keys():
                                            print(deviceData[DEVICE_NAME])                            
                                            self.devicesActives[items[0]] = d
                        except:
                            pass
              
            time.sleep(3)
                
if __name__ == '__main__':
    usbData = findUSB()
    usbData.run()
    
