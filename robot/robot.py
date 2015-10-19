#!python3
import os, sys
import queue
import shlex
import threading
import time

import zmq

from . import config
from . import logging
log = logging.logger(__package__)

class RobotError(BaseException): pass

class NoSuchActionError(RobotError): pass

class Robot(object):
    
    def __init__(
        self,
        stop_event=None,
        listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT
    ):
        log.info("Setting up Robot on %s:%s", listen_on_ip, listen_on_port)
        self.stop_event = stop_event or threading.Event()
        self._init_socket(listen_on_ip, listen_on_port)
    
    def _init_socket(self, listen_on_ip, listen_on_port):
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://%s:%s" % (listen_on_ip, listen_on_port))
    
    def get_command(self):
        """Attempt to return a unicode string from the command socket
        
        If no message was available (as opposed to a blank message) return None
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
            return message_bytes.decode(config.CODEC)
    
    def send_response(self, response):
        """Send a reply to the most recently-issued command
        """
        response_bytes = response.encode(config.CODEC)
        log.debug("About to send reponse: %r", response_bytes)
        self.socket.send(response_bytes)

    def parse_command(self, command):
        words = shlex.split(command.lower())
        return words[0], words[1:]
    
    def dispatch(self, command):
        log.debug("Dispatch on %s", command)
        if not command:
            return False, ""
        
        action, params = self.parse_command(command)
        log.debug("Action = %s, Params = %s", action, params)
        try:
            function = getattr(self, "do_" + action)
            return function(*params)
        except Exception as exc:
            log.exception("Problem executing action %s", action)
            return False, str(exc)
    
    def do_finish(self):
        self.stop_event.set()
        return True, "FINISHED"
    
    #
    # Main loop
    #
    def start(self):
        while not self.stop_event.is_set():
            try:
                command = self.get_command()
                if command is not None:
                    succeeded, response = self.dispatch(command.strip())
                    self.send_response(response)
            except KeyboardInterrupt:
                log.warn("Closing gracefully...")
                self.stop_event.set()
                break
            except:
                log.exception("Problem in main loop")
                self.stop_event.set()
                raise

if __name__ == '__main__':
    Robot().start()
