# -*- coding: utf-8 -*-
import zmq

from . import config

class SocketBase(object):
    
    def __init__(self, listen_on_ip, listen_on_port, socket_type, connect_or_bind):
        self.listen_on_ip = listen_on_ip
        self.listen_on_port = listen_on_port
        self.context = zmq.Context()
        self.socket = self.context.socket(socket_type)
        if connect_or_bind == "connect":
            self.socket.connect("tcp://%s:%s" % (self.listen_on_ip, self.listen_on_port))
        elif connect_or_bind == "bind":
            self.socket.bind("tcp://%s:%s" % (self.listen_on_ip, self.listen_on_port))
        else:
            raise RuntimeError("Can only specify connect or bind")

class Sender(SocketBase):

    def __init__(self, listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT):
        super().__init__(listen_on_ip, listen_on_port, zmq.REQ, "connect")

    def send(self, command):
        self.socket.send(command.encode(config.CODEC))
        return self.socket.recv().decode(config.CODEC)

class Publisher(SocketBase):
    
    def __init__(self, listen_on_ip=config.PUBSUB_LISTEN_ON_IP, listen_on_port=config.PUBSUB_LISTEN_ON_PORT):
        super().__init__(listen_on_ip, listen_on_port, zmq.PUB, "bind")

    def publish(self, string):
        self.socket.send_string(string)

class Subscriber(SocketBase):
    
    def __init__(self, listen_on_ip=config.PUBSUB_LISTEN_ON_IP, listen_on_port=config.PUBSUB_LISTEN_ON_PORT, subscribe_to=""):
        super().__init__(listen_on_ip, listen_on_port, zmq.SUB, "connect")
        self.subscribe(subscribe_to)

    def subscribe(self, pattern=""):
        self.socket.setsockopt_string(zmq.SUBSCRIBE, pattern)

    def __iter__(self):
        while True:
            yield socket.recv_string()
