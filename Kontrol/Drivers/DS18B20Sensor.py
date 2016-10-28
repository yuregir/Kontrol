import datetime

from twisted.logger import Logger
from w1thermsensor import W1ThermSensor

from Kontrol.Services.Core import SensorBase


class DS18B20Sensor(SensorBase):
    log = Logger()

    def __init__(self, id=0, tag='DS18B20'):
        super(DS18B20Sensor, self).__init__(tag)
        self._id = id
        self._type = 'Temperature'
        self._name = tag
        self._source = str(self)

        # TODO:Ok,I know what you're thinking:)
        self._container = dict(_id=self._id, mtype=self._type, _name=self._name, _description=str(self),
                               measurement=dict(temperature=dict(value=None,
                                                                 time=None, units='C')))
        try:
            self._driver = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, self._id)
        except Exception as e:
            # TODO: handle
            self.log.error(e.message)

    def set_value(self, d):
        # TODO: assert value
        self._container['event_type'] = 'measurement'
        self._container['measurement']['temperature']['value'] = ("%.2f" % d[0])
        self._container['measurement']['temperature']['time'] = d[1]
        return self._container

    def _update(self):
        self._return = self._driver.get_temperature()
        return self._return, str(datetime.datetime.today())

    def __repr__(self):
        return "1-W Temperature Sensor with Serial %s" % self._id
