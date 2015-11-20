# -*- coding: utf-8 -*-
import os, sys
import zmq

from . import config

#
# NB Can't use logging internally to the socket object since
# a pubsub socket is used for logging!
#

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

    def receive(self, block=False):
        flags = 0 if block else zmq.NOBLOCK
        try:
            message = self.socket.recv_string(flags, encoding=config.CODEC)
        except zmq.ZMQError as exc:
            if exc.errno == zmq.EAGAIN:
                return None
            else:
                raise
        else:
            return message

class Receiver(SocketBase):
    
    def __init__(self, listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT):
        super().__init__(listen_on_ip, listen_on_port, zmq.REP, "bind")
        
    def send(self, command):
        self.socket.send_string(command, encoding=config.CODEC)

class Sender(SocketBase):

    def __init__(self, listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT):
        super().__init__(listen_on_ip, listen_on_port, zmq.REQ, "connect")

    def send(self, command):
        self.socket.send_string(command, encoding=config.CODEC)
        return self.socket.recv_string(encoding=config.CODEC)

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
    
    def get_message(self):
        try:
            return self.socket.recv_string(zmq.NOBLOCK, encoding=config.CODEC)
        except zmq.ZMQError as exc:
            if exc.errno == zmq.EAGAIN:
                return None
            else:
                raise

    def __iter__(self):
        while True:
            message = self.get_message()
            if message:
                yield message

def demo_publish():
    import time
    publisher = Publisher()
    i = 0
    while True:
        print(i)
        publisher.publish(str(i))
        time.sleep(0.5)
        i += 1
        
def demo_subscribe(*topics):
    subscriber = Subscriber()
    print("Topics:", topics)
    if topics:
        for topic in topics:
            subscriber.subscribe(topic)
    else:
        subscriber.subscribe()
    
    print("Listening for messages...")
    for message in subscriber:
        print(message)

def demo(action="publish", *args):
    if action == "publish":
        demo_publish(*args)
    else:
        demo_subscribe(*args)

if __name__ == '__main__':
    demo(*sys.argv[1:])
