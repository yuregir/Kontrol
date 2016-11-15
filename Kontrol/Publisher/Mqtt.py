import json

from twisted.application.internet import ClientService
from twisted.logger import Logger

from Kontrol.Services.Core import PublisherBase


# ----------------
# Global variables
# ----------------

# Global object to control globally namespace logging


class MqttGatewayService(ClientService, PublisherBase):
    log = Logger()

    # TODO: Going to be removed from here!
    def init_test(self):
        if self.config:
            self.org = self.config["Globals"]["organization"]
            self.dev_id = self.config["Globals"]["device_id"]
            self.dev_type = self.config["Globals"]["device_type"]
            self.topic_pub = "eventreceiver/%s/%s/%s" % (self.org, self.dev_type, self.dev_id)
            self.topic_sub = "commandreceiver/%s/%s/%s" % (self.org, self.dev_type, self.dev_id)

        else:
            self.log.error("Config Error: Cannot get global config")

    @staticmethod
    def deunicodify_hook(pairs):
        new_pairs = []
        for key, value in pairs:
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            new_pairs.append((key, value))
        return dict(new_pairs)

    def gotProtocol(self, p):
        self.protocol = p
        d = p.connect(self.dev_id, keepalive=0)
        d.addCallback(self.subscribe)
        PublisherBase.__init__(self)
        # TODO: moveto better location
        self._name = "Mqtt Gateway"

    def publish_payload(self, data):
        self.log.debug('event received to send : {event}', event=data)
        if type(data) == dict():
            # not tested, test this if its working
            enriched_data = data.update(self.config["Globals"])
            d = self.protocol.publish(topic=self.topic_pub, message=json.dumps(enriched_data))
            d.addErrback(self.printError)
        else:
            self.log.error("Publish Error: Payload isnt a json string")

    def subscribe(self, *args):
        d = self.protocol.subscribe(self.topic_sub, 0)
        self.protocol.setPublishHandler(self.onPublish)

    def onPublish(self, topic, payload, qos, dup, retain, msgId):
        self.log.debug("msg={payload}", payload=payload)
        data_received = json.loads(str(payload), object_pairs_hook=self.deunicodify_hook)
        data_received['target'] = topic
        self._event_bus.publish_command(data_received)

    def handle_mqtt(self, data):
        print data
        # return data

    def printError(self, *args):
        self.log.debug("args={args!s}", args=args)

    @classmethod
    def connect(cls):
        # TODO: Whole rework required
        from twisted.internet import reactor
        from twisted.internet.endpoints import clientFromString
        from mqtt.client.factory import MQTTFactory

        factory = MQTTFactory(profile=MQTTFactory.PUBLISHER | MQTTFactory.SUBSCRIBER)
        mqttEndpoint = clientFromString(reactor, cls.config["Mqtt Gateway"]['server'])
        serv = MqttGatewayService(mqttEndpoint, factory)
        serv.whenConnected().addCallback(serv.gotProtocol)
        serv.startService()
