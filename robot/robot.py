#!python3
import os, sys
import queue
import threading
import time

import zmq

from . import config

def listen(
    command_queue, ack_queue, stop_event,
    listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT
):
    """Pass on commands received via zmq and pass back an acknowledgement
    """
    #
    # Create a ZMQ listening socket
    #
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://%s:%s" % (listen_on_ip, listen_on_port)
    
    #
    # 
    #
    while not stop_event().is_set():
        message = socket.recv().decode(config.CODEC)
        command_queue.put(message)
        try:
            ack = ack_queue.get(timeout=config.ACK_TIMEOUT_SECS)
            prefix = "OK"
        except queue.Empty:
            ack = b"No ack received"
            prefix = "FAIL"
        message = "%s:%s" % (prefix, ack)
        socket.send(message.encode(config.CODEC))

class Robot(object):
    
    def __init__(
        self,
        command_queue=None, ack_queue=None, stop_event=None,
        listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT
    ):
        self.command_queue = command_queue or queue.Queue()
        self.ack_queue = ack_queue or queue.Queue()
        self.stop_event = stop_event or threading.Event()
        self._init_socket(listen_on_ip, listen_on_port)
    
    def _init_socket(self, listen_on_ip, listen_on_port):
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://%s:%s" % (listen_on_ip, listen_on_port))
    
    def get_remote_message(self):
        """Attempt to return a unicode string from the command socket
        
        If no message was available (as opposed to a blank message) return None
        """
        try:
            message_bytes = self.socket.recv(zmq.NOBLOCK)
        except zmq.ZMQError as exc:
            if exc.errno == zmq.EAGAIN:
                return None
            else:
                raise
        else:
            #
            # TODO: For now, just ack straight back
            #
            self.socket.send(b"ack")
            return message_bytes.decode(config.CODEC)
    
    def start(self):
        while not self.stop_event.is_set():
            try:
                remote_message = self.get_remote_message()
                if remote_message:
                    self.command_queue.put(remote_message)
            except KeyboardInterrupt:
                self.stop_event.set()
