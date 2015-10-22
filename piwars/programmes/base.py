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

class ProgrammeError(Exception): pass

class NoSuchActionError(ProgrammeError): pass

class Programme(object):
    
    def __init__(
        self,
        robot,
        listen_on_ip=config.LISTEN_ON_IP, listen_on_port=config.LISTEN_ON_PORT
    ):
        log.info("Starting Programme on %s:%s", listen_on_ip, listen_on_port)
        log.info("Controlling %s", robot
        self.stop_event = threading.Event()
        self.command_queue = queue.Queue()
        self._init_socket(listen_on_ip, listen_on_port)
        self.robot = robot
    
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

    def get_remote_request(self):
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
    
    def parse_command(self, command):
        """Break a multi word command up into an action and its parameters
        """
        words = shlex.split(command.lower())
        return words[0], words[1:]
    
    def dispatch(self, command):
        """Pass a command along with its params to the robot
        
        If the command is blank, succeed silently
        If the command has no handler, raise NoSuchActionError
        Cascade KeyboardInterrupt
        If the handler raises an exception, fail with the exception message
        """
        log.info("Dispatch on %s", command)
        if not command:
            return "OK"
        
        action, params = self.parse_command(command)
        log.debug("Action = %s, Params = %s", action, params)
        try:
            function = getattr(self.robot, "do_" + action, None)
            if function:
                function(*params)
            else:
                raise NoSuchActionError("No such action: %s" % action)
            return "OK"
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            log.exception("Problem executing action %s", action)
            return "ERROR: %s" % exc
    
    def handle_commands(self):
        while True:
            try:
                command = self.command_queue.get_nowait()
            except queue.Empty:
                return
            else:
                self.dispatch(command)

    def queue_command(self, command):
        """Normalise and queue a non-null command.
        """
        if command is None:
            return
        else:
            self.command_queue.put(command.lowercase().strip())
    
    def generate_commands(self):
        """Pull information from whatever sources (remote commands,
        local sensors, etc.) and place commands on the queue which
        will be used to control the attached robot.
        
        The command will be normalised (lowercase, trailing whitespace
        stripped, other whitespace collapsed) and tokenised into words.
        The first word will be treated as an action to which the remaining
        words (if any) are parameters.
        
        These commands are handled by the "do_<action>" methods, to
        which the trailing parameters are passed as strings.
        
        A typical pattern will be to check for remote requests plus
        looking at sensor input to determine whether to stop, turn left
        etc.
        """
        self.queue_command(self.get_remote_request())
    
    #
    # Main loop
    #
    def start(self):
        """Handle robot commands placed on the queue by the .generate_commands
        processor specific to this programme. 
        """
        while not self.stop_event.is_set():
            try:
                self.generate_commands()
                self.handle_commands()
            except KeyboardInterrupt:
                log.warn("Closing Programme gracefully...")
                self.stop_event.set()
            except:
                log.exception("Problem in Programme")
                self.stop_event.set()
