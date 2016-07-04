import datetime
import smbus
import time

from twisted.logger import Logger

from Kontrol.Services.Core import SensorBase


class ChirpSensor(SensorBase):
    log = Logger()

    def __init__(self, bus=1, address=0x20, tag='SoilMoist'):
        super(ChirpSensor, self).__init__()
        self._type = 'Chirp'
        self._i2c_bus = bus
        self._driver = smbus.SMBus(bus)
        self._i2c_addr = address
        self._name = tag
        self._id = str(self._i2c_bus) + str(self._i2c_addr)
        self._source = str(self)
        self._container = dict(_id=self._id, _type=self._type, _name=self._name, _description=str(self),
                               measurement=dict(
                                   soilmoisture=dict(value=None, time=None, units='%'),
                                   temperature=dict(value=None, time=None, units='C'),
                                   light=dict(value=None, time=None, units='Lux')))

    def get_reg(self, reg):
        # read 2 bytes from register
        val = self._driver.read_word_data(self._i2c_addr, reg)
        # return swapped bytes (they come in wrong order)
        return (val >> 8) + ((val & 0xFF) << 8)

    def reset(self):
        # To reset the sensor, write 6 to the device I2C address
        self._driver.write_byte(self._i2c_addr, 6)

    def set_addr(self, new_addr):
        # To change the I2C address of the sensor, write a new address
        # (one byte [1..127]) to register 1; the new address will take effect after reset
        self._driver.write_byte_data(self._i2c_addr, 1, new_addr)
        self.reset()
        self._i2c_addr = new_addr

    def moist(self):
        # To read soil moisture, read 2 bytes from register 0
        return self.get_reg(0)

    def temp(self):
        # To read temperature, read 2 bytes from register 5
        return self.get_reg(5)

    def light(self):
        # To read light level, start measurement by writing 3 to the
        # device I2C address, wait for 3 seconds, read 2 bytes from register 4
        self._driver.write_byte(self._i2c_addr, 3)
        time.sleep(3)
        return self.get_reg(4)

    def _update(self):
        self._return = (self.moist() - 300) / 4.8, self.temp(), self.light(), str(datetime.datetime.today())
        return self._return

    def set_value(self, d):
        # TODO: assert value
        self._container['event_type'] = 'measurement'
        self._container['measurement']['soilmoisture']['value'] = ("%.2f" % d[0])
        self._container['measurement']['soilmoisture']['time'] = d[3]
        self._container['measurement']['temperature']['value'] = ("%.2f" % d[1])
        self._container['measurement']['temperature']['time'] = d[3]
        self._container['measurement']['light']['value'] = ("%.2f" % d[2])
        self._container['measurement']['light']['time'] = d[3]

        return self._container

    def debug(self):
        print self._update()

    def __repr__(self):
        return "Chirp Soil Moisture Sensor on bus %s with address %s" % (self._i2c_bus, self._i2c_addr)
