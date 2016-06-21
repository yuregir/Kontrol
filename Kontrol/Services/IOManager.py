from Kontrol.Services.Core import ServiceBase
import Adafruit_BBIO.GPIO as GPIO
import datetime
from twisted.logger import Logger


class DigitalOutput(ServiceBase):
    log = Logger()

    def __init__(self, pin, inv=True):
        super(DigitalOutput, self).__init__()
        self._pin = pin
        self._name = pin
        self._tag = pin
        self._inv = inv
        self._type = 'Digital Output Instance Service'
        self._on = GPIO.HIGH
        self._off = GPIO.LOW
        self._capabilities = {'turn_on': self.turn_on,
                              'turn_off': self.turn_off,
                              'status': self.status,
                              'set_name': self.set_name,
                              'set_direction': self.set_direction,
                              'get_capabilities': self.get_capabilities}

        self.set_direction(inv)
        # TODO: This is beta call, GPIO
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin, self._off)

    def get_capabilities(self):
        return self._capabilities

    #    def command_handler(self, command):
    #        self.log.debug("Command received from {pin_name} : {command}", pin_name=self.get_name, command=str(command))

    def set_name(self, name):
        self._name = name

    def status(self):
        state = {
            'source': self,
            'type': self._type,
            'name': self._name,
            'pin_name': self._pin,
            'state': GPIO.input(self._pin),
            'time': str(datetime.datetime.today())
        }
        return state

    def set_direction(self, direction):
        if direction:
            self._on, self._off = GPIO.HIGH, GPIO.LOW
            self.log.debug('Setting output {output} signal type as inverted.', output=self._pin)
        else:
            self._on, self._off = GPIO.LOW, GPIO.HIGH
            self.log.debug('Setting output {output} signal type as NOT inverted.', output=self._pin)

    @property
    def get_name(self):
        return self._name

    def turn_on(self):
        self._state['lastchange'] = str(datetime.datetime.today())
        print 'vars pin on', self._pin, self._on
        GPIO.output(self._pin, self._on)
        self.log.info('Turning {pin} on...', pin=self._pin)

        self._event_bus.publish_sensor(self.state)

    def turn_off(self):
        print 'turning off'
        self._state['lastchange'] = str(datetime.datetime.today())
        GPIO.output(self._pin, self._off)
        self.verify_state(self._off)
        self._event_bus.publish_sensor(self.state)

    def verify_state(self, state):
        if state == GPIO.input(self._pin):
            self.log.debug('Pin state changed successfully.')
            return True
        else:
            self.log.error('State change FAILED on pin: {pin}', pin=self._pin)
            self.log.debug('Requested state: {reqst}, current state: {curst}}', reqst=state,
                           curst=GPIO.input(self._pin))
            return False

    @property
    def pin_name(self):
        return self._pin
