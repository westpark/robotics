# -*- coding: utf-8 -*-
import zmq

from ..core import config

class Sender(object):
    
    def __init__(self, listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT):
        self.listen_on_ip = listen_on_ip
        self.listen_on_port = listen_on_port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://%s:%s" % (self.listen_on_ip, self.listen_on_port))

    def send(self, command):
        self.socket.send(command.encode(config.CODEC))
        return self.socket.recv().decode(config.CODEC)
