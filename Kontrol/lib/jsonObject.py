def decode_unicode(pairs):
    new_pairs = []
    for key, value in pairs:
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        new_pairs.append((key, value))
    return dict(new_pairs)


class JSONObject:
    def __init__(self, d):
        self.__dict__ = d


class Measurement(JSONObject):
    def __init__(self):
        self._type = 'Measurement'
        self._measurement = {'measurement': dict()}

    def set_measurement(self, measurement_name, value):

        self._measurement[measurement_name] = value

    def get_measurement(self, measurement_name):
        try:
            return self._measurement[measurement_name]
        except Exception as e:
            return e.message

    def get_all(self):
        try:
            return self._measurement
        except Exception as e:
            return e.message

    def del_measurement(self, measurement_name):
        try:
            self._measurement.pop(measurement_name)
        except Exception as e:
            return e.message
