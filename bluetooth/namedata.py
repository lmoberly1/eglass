#!/usr/bin/python3

import dbus
import time
import random

from bluetooth.advertisement import Advertisement
from bluetooth.service import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000

class NameAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("Names")
        self.include_tx_power = True

class NameService(Service):
    NAME_SVC_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, index):
        self.names = []

        Service.__init__(self, index, self.NAME_SVC_UUID, True)
        self.add_characteristic(NameCharacteristic(self))
    
    def set_name(self, names):
        print('SETTING NAMES', names)
        self.names = names
    
    def read_names(self):
        return self.names



class NameCharacteristic(Characteristic):
    NAME_CHARACTERISTIC_UUID = "00000002-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
                self, self.NAME_CHARACTERISTIC_UUID,
                ["notify", "read"], service)
        self.add_descriptor(NameDescriptor(self))


    def get_names(self):
        value = []
        names = self.service.read_names()
        print('GETTING NAMES', names)

        for c in names:
            value.append(dbus.Byte(c.encode()))

        return value

    def set_name_callback(self):
        if self.notifying:
            value = self.get_names()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        print('Now notifying on peripheral')

        value = self.get_names()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_name_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        value = self.get_names()

        return value

class NameDescriptor(Descriptor):
    NAME_DESCRIPTOR_UUID = "2901"
    NAME_DESCRIPTOR_VALUE = "Names on Screen"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.NAME_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.NAME_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value



# app = Application()
# app.add_service(NameService(0))
# app.register()

# adv = NameAdvertisement(0)
# adv.register()

# try:
#     app.run()
# except KeyboardInterrupt:
#     app.quit()
