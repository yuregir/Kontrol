import random
import sys

from cyrusbus import Bus
from twisted.internet import reactor
from twisted.internet import threads
from twisted.internet.defer import Deferred


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EventBus(object):
    __metaclass__ = Singleton
    _bus = Bus()
    _event_bus = None

    def __init__(self):
        # TODO: convert to singleton
        self._bus = type(self)._bus
        self._channel = 'default/'
        self._log_channel_key = 'log/'
        self._sensor_channel_key = 'sensor/'
        self._event_channel_key = 'event/'
        self._service_channel_key = 'command/'
        # FIXME
        if not type(self)._event_bus:
            type(self)._event_bus = self
        self._event_bus = type(self)._event_bus

        # self._name = 'Internal Event Bus Service'
        # self._tag = 'EVB'
        # TODO: Not completed yet
        # self._capabilities = {'get_nodes': self.register_sensorbus,
        #                      'get_eventbus_services': self.register_sensorbus,
        #                      'get_commandbus_services': self.register_sensorbus,
        #                      'get_logbus_services': self.register_sensorbus,
        #                      }
        # self._container = {}
        self.log.info('EventBus Initialized')

    # TODO: NOT COMPLETE !!!
    def get_nodes(self):
        return

    def get_commandbus_services(self):
        return

    def get_eventbus_services(self):
        return

    def get_logbus_services(self):
        return

    def register_sensorbus(self, callback):
        self._bus.subscribe(self._sensor_channel_key, callback)
        self.log.debug(' registered to sensor bus.')
        # todo: log subs

    def register_eventbus(self, callback):
        self._bus.subscribe(self._event_channel_key, callback)
        self.log.debug(' registered to event bus.')
        # todo: log subs

    def register_logbus(self, callback):
        self._bus.subscribe(self._log_channel_key, callback)
        self.log.debug(' registered to error bus.')
        # todo: log subs

    def register_commandbus(self, callback):
        self._bus.subscribe(self._service_channel_key, callback)
        self.log.debug(' registered to command bus.')
        # todo: log subs

    def unregister(self, channel, callback):
        # todo: log unsub

        self._bus.unsubscribe(channel, callback)
        self.log.debug('%s unregistered from %s') % (str(callback), channel)

    def publish_sensor(self, data):
        self._bus.publish(self._sensor_channel_key, data)

    def publish_log(self, data):
        self._bus.publish(self._log_channel_key, data)

    def publish_event(self, data):
        self._bus.publish(self._event_channel_key, data)

    def publish_command(self, data):
        self._bus.publish(self._service_channel_key, data)


class ServiceBase(EventBus):
    config = None
    def __init__(self):
        super(ServiceBase, self).__init__()
        self._type = "Service"
        self._capabilities = {}
        self._data_counter = {"in": 0, "out": 0}

        self._event_bus.register_commandbus(self.commandReceived)

    def data_in_counter(self, data):
        self._data_counter['in'] += sys.getsizeof(data)
        return data

    def data_out_counter(self, data):
        self._data_counter['out'] += sys.getsizeof(data)
        return data

    def commandReceived(self, bus, data):
        d = Deferred()
        d.addCallback(self.data_in_counter)
        d.addErrback(self.error_handler)
        d.addCallback(self.command_handler)
        d.callback(data)

    # FIXME: for debug purposes
    def command_handler(self, command):
        self.log.debug("Command received from {type}.{name} : {command}", type=self._type, name=self._name,
                       command=str(command))
        if command['command'] in self._capabilities:
            print '***'
            d = self._capabilities[command['command']]()
            self._event_bus.publish_sensor(d)
        else:
            print('*** DBG:not capable of cmd', 'capabilities: ', self._capabilities, 'sent cmd: ', command['command'])

    # def command_handler(self, command):
    #     # This must be overriden with your command handler code, this method calls on every message if target==self._name
    #     raise NotImplementedError(
    #         message="This must be overriden with your command handler code, this method calls on every message if target==self._name")

    def error_handler(self, error):
        self.log.debug(str(error.getErrorMessage))


class PublisherBase(ServiceBase):
    def __init__(self):
        super(PublisherBase, self).__init__()
        self._type = 'Publisher'
        self._name = 'Base Publisher Service'
        self.register_sensorbus(self.eventbus_handler)

    def eventbus_handler(self, bus, data):
        d = Deferred()
        d.addCallback(self.data_out_counter)
        d.addCallback(self.publish_payload)
        d.addErrback(self.error_handler)
        d.callback(data)

    def publish_payload(self, data):
        pass


class SensorBase(ServiceBase):
    def __init__(self, tag='Default'):
        super(SensorBase, self).__init__()
        self._name = 'Base Sensor'
        self._tag = tag
        self._value = None
        self._timestamp = None
        self._refresh = 30
        self._container = dict()
        self._statics = {'Q_tot': 0, 'Q_suc': 0, 'Q_err': 0}
        self._type = 'Sensor'
        self._state = 'initializing'
        self._capabilities = {'start': self.start,
                              'stop': self.stop,
                              'status': self.status,
                              'set_refresh': self.set_refresh
                              }

    def set_refresh(self, rate):
        self._refresh = rate

    def start(self):
        self._state = 'running'
        self.log.info('Starting {sensor_name} service...', sensor_name=self._name)
        # not to poll at same time
        reactor.callLater(random.randint(5, 25), self._looping_poll_blocking)
        # return self._state

    def stop(self):
        self.log.info('Stopping {sensor_name} service...', sensor_name=self._name)
        self._state = 'stopped'
        # return self._state

    def status(self):
        # print('DBG-Q: ', self._statics['Q_err'], self._statics['Q_suc'])
        data = {'source': self._tag,
                'Service Status': self._state,
                'Capabilities': self._capabilities.keys(),
                'Health': [self._statics['Q_err'], self._statics['Q_suc']],
                'Traffic in/out': [self._data_counter['in'], self._data_counter['out']],
                'Last Readings:': self.value
                }
        return data

    def _looping_poll_blocking(self):
        # self.debug()
        if self._state == 'running':
            self.log.debug('Polling {name} sensor...', name=self._name)
            reactor.callLater(self._refresh, self._looping_poll_blocking)
        d = threads.deferToThread(self._update)
        d.addCallback(self.set_value)
        d.addErrback(self._sensor_error)
        d.addCallback(self._handle_success)
        d.addBoth(self.notify)
        return d

    def _sensor_error(self, error):
        self.log.debug('Sensor communication failure! ', failiure=error)
        self._container['errors'] = [str(error.getErrorMessage())]
        self._statics['Q_err'] += 1

    def _handle_success(self, d):
        self.log.debug('Got measurement from {name} sensor...', name=self._name)
        self._statics['Q_suc'] += 1
        return d

    def set_value(self, d):
        # TODO: assert value

        self.log.debug("This shouldnt supposed to run")

    def notify(self, d):
        # not needed
        self.log.debug('Sending {name} sensor measurement to eventbus...', name=self._name)
        self._event_bus.publish_sensor(self.value)
        return d

    @property
    def value(self):
        return self._container

    def _update(self):
        self.log.error('{sensor_name} update feature is NOT implemented yet, you need to override this method',
                       sensor_name=self._name)
