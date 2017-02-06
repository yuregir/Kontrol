import datetime

from twisted.logger import Logger
from Kontrol.Services.Core import SensorBase
from random import randint


class DummySensor(SensorBase):
    log = Logger()

    def __init__(self, id=0, tag='Dummy'):
        super(DummySensor, self).__init__(tag)
        self._id = randint(1000, 9999)
        self._type = 'dummy'
        self._name = tag
        self._source = str(self)

    def set_value(self, d):
        # TODO: assert value
        self._container['event_type'] = 'measurement'
        self._container['measurement']['dummy']['value'] = (d[0])
        self._container['measurement']['dummy']['time'] = d[1]
        return self._container

    def _update(self):
        self._return = randint(0, 100)
        return self._return, str(datetime.datetime.today())

    def __repr__(self):
        return "Dummy Sensor with Serial %s" % self._id
