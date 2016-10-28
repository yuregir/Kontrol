import sys

from twisted.internet import reactor, task
from twisted.application.internet import ClientService
from twisted.internet.endpoints import clientFromString
from twisted.logger import (
    Logger, LogLevel, globalLogBeginner, textFileLogObserver,
    FilteringLogObserver, LogLevelFilterPredicate)

from mqtt.client.factory import MQTTFactory
import minimalmodbus

# ----------------
# Global variables
# ----------------

# Global object to control globally namespace logging
logLevelFilterPredicate = LogLevelFilterPredicate(defaultLogLevel=LogLevel.info)


# -----------------
# Utility Functions
# -----------------

def startLogging(console=True, filepath=None):
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


def setLogLevel(namespace=None, levelStr='info'):
    '''
    Set a new log level for a given namespace
    LevelStr is: 'critical', 'error', 'warn', 'info', 'debug'
    '''
    level = LogLevel.levelWithName(levelStr)
    logLevelFilterPredicate.setLogLevelForNamespace(namespace=namespace, level=level)


class MyService(ClientService):
    def gotProtocol(self, p):
        self.protocol = p
        d = p.connect("TwistedMQTT-pubsubs", keepalive=0)
        d.addCallback(self.subscribe)
        d.addCallback(self.prepareToPublish)

    def subscribe(self, *args):
        d = self.protocol.subscribe("windeventmanager/windturbine/01/command", 0)
        self.protocol.setPublishHandler(self.onPublish)

    def onPublish(self, topic, payload, qos, dup, retain, msgId):
        log.debug("msg={payload}", payload=payload)

    def prepareToPublish(self, *args):
        self.task = task.LoopingCall(self.publish)
        self.task.start(5.0)

    def publish(self):
        d = self.protocol.publish(topic="foo/bar/baz", message="hello friends")
        d.addErrback(self.printError)

    def printError(self, *args):
        log.debug("args={args!s}", args=args)
        reactor.stop()

    def init_modbus(self):
        self.instrument = minimalmodbus.Instrument('/dev/tty.wchusbserial1410', 1)
        self.supported_commands = {"set_temps" =}

        def read_modbus_temps(self):

            self.start_temp = self.instrument.read_register(218, 2) * 10
            self.stop_temp = self.instrument.read_register(219, 2) * 10
            d = self.protocol.publish(topic="windeventmanager/windturbine/01/measurement/start_temp",
                                      message=self.start_temp)
            d = self.protocol.publish(topic="windeventmanager/windturbine/01/measurement/stop_temp",
                                      message=self.stop_temp)

            # return self.start_temp,self.stop_temp

        def handle_command(self, command):
            if command in self.supported_commands:
                self.supported_commands[command]
            else:
                print "unknown command: ", command

        def write_modbus_temps(self, start_new, stop_new):
            self.instrument.write_register(218, start_new, 2)

            self.instrument.write_register(219, stop_new, 2)

    if __name__ == '__main__':
        import sys
        log = Logger()
        startLogging()
        setLogLevel(namespace='mqtt', levelStr='debug')
        setLogLevel(namespace='__main__', levelStr='debug')

        factory = MQTTFactory(profile=MQTTFactory.PUBLISHER | MQTTFactory.SUBSCRIBER)
        myEndpoint = clientFromString(reactor, "tcp:metrics.sipsunucu.com:1883")
        serv = MyService(myEndpoint, factory)
        serv.whenConnected().addCallback(serv.gotProtocol)
        serv.startService()
        reactor.run()
