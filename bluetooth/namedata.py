#!/usr/bin/python3

"""Copyright (c) 2019, Douglas Otwell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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
        self.add_local_name("Names") # CHANGED
        self.include_tx_power = True

class NameService(Service):
    NAME_SVC_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, index):
        self.name = ''

        Service.__init__(self, index, self.NAME_SVC_UUID, True)
        self.add_characteristic(NameCharacteristic(self))
    
    def set_name(self, name):
        self.name = name


class NameCharacteristic(Characteristic):
    NAME_CHARACTERISTIC_UUID = "00000002-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
                self, self.NAME_CHARACTERISTIC_UUID,
                ["notify", "read"], service)
        self.add_descriptor(NameDescriptor(self))


    def get_name(self):
        print("getting name")
        names = ['Luke', 'Emma', 'Henry', 'Daniel', 'Griffin']

        # get random name from array
        name = random.choice(names)
        self.service.set_name(name)

        value = []
        name = self.service.name

        for c in name:
            value.append(dbus.Byte(c.encode()))

        return value

    def set_name_callback(self):
        if self.notifying:
            value = self.get_name()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        print('Now notifying on peripheral')

        value = self.get_name()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_name_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        value = self.get_name()

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
