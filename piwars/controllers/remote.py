# -*- coding: utf-8 -*-
import os, sys
import fnmatch
import queue
import shlex
import threading
import time

import zmq

from ..core import comms, config, exc, logging
from . import base
log = logging.logger(__package__)

class Controller(base.Controller):
    
    _permitted_commands = ["*"]
    
    def __init__(
        self,
        robot,
        listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT
    ):
        super().__init__(robot)
        self.socket = comms.Receiver(listen_on_ip, listen_on_port)
    
    def get_remote_request(self):
        """Attempt to return a unicode object from the command socket
        
        If no message is available without blocking (as opposed to a blank 
        message), return None
        """
        return self.socket.receive(block=True)
    
    def send_remote_response(self, response):
        """Send a unicode object as reply to the most recently-issued command
        """
        self.socket.send(response)

    def get_request(self):
        """Respond immediately to an incoming request and pass back the command received
        
        The REP/REQ socket model we're using with zmq requires that each
        send is paired with a recv. For now, make sure that works by always
        replying immediately to an incoming request. Later we might tag the
        command passed back so we know we need to generate a reply at some
        later point, eg when the command has been processed.
        """
        command = self.get_remote_request()
        self.send_remote_response("ACK")
        return command

    def generate_commands(self):
        super().generate_commands()
        command = self.get_request()
        if command:
            log.info("Received command: %s", command)
            action, params = self.parse_command(command)
            if any(fnmatch.fnmatch(action, c) for c in self._permitted_commands):
                self.queue_command(action, params)
