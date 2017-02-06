
import sys

from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


from twisted.internet import reactor
from twisted.logger import Logger, LogLevelFilterPredicate, textFileLogObserver, FilteringLogObserver, \
    globalLogBeginner, LogLevel
# from Kontrol.Drivers.BME280Sensor import BME280Sensor
# from Kontrol.Drivers.ChirpSensor import ChirpSensor
# from Kontrol.Drivers.DS18B20Sensor import DS18B20Sensor
from Kontrol.Publisher.Mqtt import MqttGatewayService
from Kontrol.Services.DeviceManager import DeviceManager

#from Kontrol.Services.IOManager import DigitalOutput

# ----------------------
# Log Utility Functions
# ----------------------


log = Logger()
logLevelFilterPredicate = LogLevelFilterPredicate(defaultLogLevel=LogLevel.debug)


def startLogging(console=True, filepath='./kontrol.log'):
    '''
    Starts the global Twisted logger subsystem with maybe
    stdout and/or a file specified in the config file
    '''
    global logLevelFilterPredicate

    observers = []
    if console:
        observers.append(FilteringLogObserver(observer=textFileLogObserver(sys.stdout),
                                              predicates=[logLevelFilterPredicate]))

    if filepath is not None and filepath != "":
        observers.append(FilteringLogObserver(observer=textFileLogObserver(open(filepath, 'a')),
                                              predicates=[logLevelFilterPredicate]))
    globalLogBeginner.beginLoggingTo(observers)


def setLogLevel(namespace=None, levelStr='debug'):
    '''
    Set a new log level for a given namespace
    LevelStr is: 'critical', 'error', 'warn', 'info', 'debug'
    '''
    level = LogLevel.levelWithName(levelStr)
    logLevelFilterPredicate.setLogLevelForNamespace(namespace=namespace, level=level)


# def mqtt_start():
#     from twisted.internet.endpoints import clientFromString
#
#     from mqtt.client.factory import MQTTFactory
#     startLogging()
#     factory = MQTTFactory(profile=MQTTFactory.PUBLISHER | MQTTFactory.SUBSCRIBER)
#     myEndpoint = clientFromString(reactor, config_mqtt['server'])
#     serv = MqttGatewayService(myEndpoint, factory)
#     serv.whenConnected().addCallback(serv.gotProtocol)
#    serv.startService()



# ------------
#   API Init
# ------------

startLogging()
device = DeviceManager('config.json')
device.start()

reactor.callLater(5, MqttGatewayService.connect)


# startLogging()
reactor.run()
