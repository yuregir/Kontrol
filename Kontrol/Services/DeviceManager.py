from Core import ServiceBase
import json
# change to smbus when uploading
import smbus
from twisted.logger import Logger
from Kontrol.Drivers import DS18B20Sensor, BME280Sensor, ChirpSensor


class DeviceManager(ServiceBase):
    log = Logger()

    def __init__(self):
        # global log
        super(DeviceManager, self).__init__()
        self._name = 'Device Manager'
        self._tag = 'DM'
        self._config = None
        self._i2c_devices = {}
        self._w1_devices = {}
        self._capabilities = {'load_config': self.load_config,
                              'refresh_config': None,
                              'get_i2c_devices': self.get_i2c_devices,
                              'get_w1_devices': self.get_w1_devices,
                              'status': self.status}
        self._IO_devices = {}
        self._drivers = {}
        self._state = 'Init'
        ##register callback to command bus

    def start(self):

        self._state = 'Start'
        self.log.info('Starting Core Services...')

    def status(self):
        return {'w1': self.get_w1_devices(), 'i2c': self.get_i2c_devices()}

    def load_config(self, config):
        try:
            self._config = json.loads(config)
        except Exception as e:
            self.log.failure('Invalid config', failure=e)

    def get_IO_devices(self):
        pass

    def get_driver(self, driver):
        pass

    def list_drivers(self):
        return self._drivers

    def command_handler(self, command):
        print("*_*_*_*Comm rcvd : ", command)

    def get_i2c_devices(self, bus_list=[0, 1]):
        self.log.debug('Scanning for i2c devices.')
        devices_count = 0
        for busnum in bus_list:
            bus = smbus.SMBus(busnum)

            for device in range(128):

                try:
                    bus.read_byte(device)
                    self.log.debug('Device detected on bus {busnum} with {id}.', busnum=busnum, id=hex(device))
                    id = str(busnum) + str(device)
                    self._i2c_devices[devices_count] = {'id': id,
                                                        'bus_id': busnum,
                                                        'bus_address': device,
                                                        'type': 'i2c device'}
                    devices_count += 1
                except:  # exception if read_byte fails
                    pass

        self.log.debug('I2c scan finished.')
        return self._i2c_devices

    # TODO: not completed

    def get_w1_devices(self):
        self.log.debug('Scanning for 1W devices.')
        # for sensor in W1ThermSensor.get_available_sensors():
        #    self._w1_devices[sensor.id] = {'id': sensor.id, 'type': '1-Wire device'}
        # return self._w1_devices

    # TODO: not completed
    def setup_w1_device(self, serial, driver='ds18b20'):
        # Todo: change this later to driver dict!
        # if driver == 'ds18b20':
        #     try:
        #         temp_sensor = TempSensor(id, self._bus)
        #     except:
        #         self.log.error('Could not communicate with sensor serial: {serial}, driver: {drv}.',
        #                   serial=serial, drv=driver)
        #         temp_sensor = None
        #     finally:
        #         return temp_sensor
        #
        # else:
        #     self.log.error("Unknown Driver {driver_name}", driver_name=driver)
        #     return None
        return
