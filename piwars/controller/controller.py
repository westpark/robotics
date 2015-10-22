# -*- coding: utf-8 -*-
import os, sys
import queue
import shlex
import threading
import time

import zmq

from ..core import config
from ..core import logging
log = logging.logger(__package__)

class ControllerError(Exception): pass

class NoSuchActionError(ControllerError): pass

class Controller(object):
    
    def __init__(
        self,
        robot,
        listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT
    ):
        log.info("Starting controller on %s:%s", listen_on_ip, listen_on_port)
        log.info("Controlling %s", robot
        self.stop_event = threading.Event()
        self._init_socket(listen_on_ip, listen_on_port)
        self.robot = robot
        self.robot._init()
    
    def _init_socket(self, listen_on_ip, listen_on_port):
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://%s:%s" % (listen_on_ip, listen_on_port))
    
    def get_command(self):
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
            return message_bytes.decode(config.CODEC)
    
    def send_response(self, response):
        """Send a unicode object as reply to the most recently-issued command
        """
        response_bytes = response.encode(config.CODEC)
        log.debug("About to send reponse: %r", response_bytes)
        self.socket.send(response_bytes)

    def parse_command(self, command):
        """Break a multi word command up into an action and its parameters
        """
        words = shlex.split(command.lower())
        return words[0], words[1:]
    
    def dispatch(self, command):
        """Pass a command along with its params to a suitable handler
        
        If the command is blank, succeed silently
        If the command has no handler, succeed silently
        If the handler raises an exception, fail with the exception message
        """
        log.info("Dispatch on %s", command)
        if not command:
            return "OK"
        
        action, params = self.parse_command(command)
        log.debug("Action = %s, Params = %s", action, params)
        try:
            function = getattr(self, "do_" + action, None)
            if function:
                function(*params)
            return "OK"
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            log.exception("Problem executing action %s", action)
            return "ERROR: %s" % exc
    
    def do_robot(self, *args):
        """Pass a command directly to the current robot processor
        """
        if args:
            action, params = args[0], args[1:]
            log.debug("Pass %s directly to robot with %s", action, params)
            function = getattr(self.robot, "do_" + action, None)
            if function:
                function(*params)
    
    def do_finish(self):
        self.stop_event.set()
    
    #
    # Main loop
    #
    def start(self):
        while not self.stop_event.is_set():
            try:
                command = self.get_command()
                if command is not None:
                    response = self.dispatch(command.strip())
                    self.send_response(response)
            except KeyboardInterrupt:
                log.warn("Closing controller gracefully...")
                self.stop_event.set()
                break
            except:
                log.exception("Problem in controller")
                self.stop_event.set()
                raise

