# -*- coding: utf-8 -*-
import os, sys
import queue
import shlex
import threading
import time

import zmq

from ..core import config, exc, logging
log = logging.logger(__package__)
from .. import robots

class ControllerError(exc.PiWarsError): pass
class NoSuchActionError(ControllerError): pass
class NoSuchRobotError(ControllerError): pass

class Controller(object):
    
    def __init__(self, robot):
        log.info("Starting Controller on %s:%s", listen_on_ip, listen_on_port)
        log.info("Controlling %s", robot
        self.stop_event = threading.Event()
        self.command_queue = queue.Queue()
        self.robot = robot
    
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
        pass
    
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
                log.warn("Closing Controller gracefully...")
                self.stop_event.set()
            except:
                log.exception("Problem in Controller")
                self.stop_event.set()

