import datetime

from twisted.logger import Logger
from w1thermsensor import W1ThermSensor

from Kontrol.Services.Core import SensorBase


class DS18B20Sensor(SensorBase):
    log = Logger()

    def __init__(self, id=0, tag='DS18B20'):
        super(DS18B20Sensor, self).__init__(tag)
        self._id = id
        self._type = 'temperature'
        self._name = tag
        self._source = str(self)
        self._container = {}
        try:
            self._driver = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, self._id)
        except Exception as e:
            # TODO: handle
            self.log.error(e.message)

    def set_value(self, d):
        # TODO: assert value
        self.log.debug("DeBug:setting value: " + str(d))
        self._container['event_type'] = 'measurement'
        self._container['temperature'] = ("%.2f" % d[0])
        self._container['time'] = d[1]
        print(self._container)
        return self._container

    def _update(self):
        self._return = self._driver.get_temperature()
        self.log.debug(str(self._return))
        return self._return, str(datetime.datetime.today())

    def __repr__(self):
        return "1-W Temperature Sensor with Serial %s" % self._id
