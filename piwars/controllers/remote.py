# -*- coding: utf-8 -*-
import os, sys
import queue
import shlex
import threading
import time

import zmq

from ..core import config, exc, logging
from . import base
log = logging.logger(__package__)

class Controller(base.Controller):
    
    def __init__(
        self,
        robot,
        listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT
    ):
        super().__init__(robot)
        log.info("Starting Controller on %s:%s", listen_on_ip, listen_on_port)
        self._init_socket(listen_on_ip, listen_on_port)
    
    def _init_socket(self, listen_on_ip, listen_on_port):
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://%s:%s" % (listen_on_ip, listen_on_port))
    
    def get_remote_request(self):
        """Attempt to return a unicode object from the command socket
        
        If no message is available without blocking (as opposed to a blank 
        message), return None
        """
        try:
            message_bytes = self.socket.recv(zmq.NOBLOCK)
            log.debug("Received message: %r", message_bytes)
        except zmq.ZMQError as exc:
            if exc.errno == zmq.EAGAIN:
                return None
            else:
                raise
        else:
            return message_bytes.decode(config.CODEC).strip().lower()
    
    def send_remote_response(self, response):
        """Send a unicode object as reply to the most recently-issued command
        """
        response_bytes = response.strip().lower().encode(config.CODEC)
        log.debug("About to send reponse: %r", response_bytes)
        self.socket.send(response_bytes)

    def get_request(self):
        """Respond immediately to an incoming request and pass back the command received
        
        The REP/REQ socket model we're using with zmq requires that each
        send is paired with a recv. For now, make sure that works by always
        replying immediately to an incoming request. Later we might tag the
        command passed back so we know we need to generate a reply at some
        later point, eg when the command has been processed.
        """
        command = self.get_remote_request()
        #
        # get_remote_request returns None if there was no message
        # waiting on the socket.
        #
        if command is not None:
            self.send_remote_response("OK " + command)
            return command

    def generate_commands(self):
        super().generate_commands()
        self.queue_command(self.get_request())
    
