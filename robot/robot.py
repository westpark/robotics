#!python3
import os, sys
import queue
import threading
import time

import zmq

from . import config

def listen(
    command_queue, ack_queue, 
    listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT
):
    """Pass on commands received via zmq and pass back an acknowledgement
    """
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://%s:%s" % (listen_on_ip, listen_on_port)
    
    while True:
        message = socket.recv()
        command_queue.put(message)
        try:
            ack = ack_queue.get(timeout=config.ACK_TIMEOUT_SECS)
            prefix = "OK"
        except queue.Empty:
            ack = b"No ack received"
            prefix = "FAIL"
        socket.send(b"%s:%s" % (prefix, ack))

class Robot(object):
    
    def __init__(self):
        pass