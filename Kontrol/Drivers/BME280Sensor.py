import datetime

from twisted.logger import Logger

from Adafruit_BME280 import *
from Kontrol.Services.Core import SensorBase


class BME280Sensor(SensorBase):
    log = Logger()

    def __init__(self, bus=1, address=0x77, tag='Combined Weather Sensor'):
        super(BME280Sensor, self).__init__()
        self._type = 'weatherSensor'
        self._i2c_bus = bus
        self._driver = BME280(mode=BME280_OSAMPLE_8)
        self._i2c_addr = address
        self._name = tag
        self._tag = tag
        self._id = str(self._i2c_bus) + str(self._i2c_addr)
        self._source = str(self)
        self._container = dict(_id=self._id, mtype=self._type, _name=self._name, _description=str(self),
                               measurement=dict(
                                   airhumidity=dict(value=None, time=None, units='%'),
                                   airtemperature=dict(value=None, time=None, units='C'),
                                   airpressure=dict(value=None, time=None, units='KPa')))

    def set_value(self, d):
        # TODO: assert value

        self._container['event_type'] = 'measurement'
        self._container['measurement']['airhumidity']['value'] = ("%.2f" % d[0])
        self._container['measurement']['airhumidity']['time'] = d[3]
        self._container['measurement']['airtemperature']['value'] = ("%.2f" % d[1])
        self._container['measurement']['airtemperature']['time'] = d[3]
        self._container['measurement']['airpressure']['value'] = "%.2f" % (d[2] / 1000)
        self._container['measurement']['airpressure']['time'] = d[3]

        return self._container

    def _update(self):
        self._return = (self._driver.read_humidity(), self._driver.read_temperature(),
                        self._driver.read_pressure(), str(datetime.datetime.today()))
        return self._return

    def __repr__(self):
        return "BME280 Weather Sensor on bus %s with address %s" % (self._i2c_bus, self._i2c_addr)
