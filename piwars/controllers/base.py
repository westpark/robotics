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
    """A controller is effectively a program running on the robot. It receives
    a queue of commands, and either handles each one internally or passes it onto
    the robot it was started with.
    
    Commands are a series of space-separated words, encoded according to config.ENCODING.
    The first word is the action; all other words (if any) are passed along as parameters.
    """
    
    def __init__(self, robot):
        log.info("Controlling %s", robot)
        self.stop_event = threading.Event()
        self.command_queue = queue.Queue()
        self.robot = robot
    
    def parse_command(self, command):
        """Break a multi word command up into an action and its parameters
        """
        words = shlex.split(command.lower())
        return words[0], words[1:]
    
    def dispatch(self, action, params):
        """Pass a command along with its params to the robot
        
        If the command is blank, succeed silently
        Look for a handler (1) in the current controller; (2) in the current controller's robot
        If the command has no handler, raise NoSuchActionError
        Cascade KeyboardInterrupt
        If the handler raises an exception, fail with the exception message
        """
        log.info("Dispatch on %s: %s", action, params)
        if not action:
            return
        
        log.debug("Action = %s, Params = %s", action, params)
        try:
            function = getattr(self, "handle_%s" % action, None)
            if not function:
                function = getattr(self.robot, action, None)
            if function:
                function(*params)
            else:
                log.warn("No such action: %s", action)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            log.exception("Problem executing action %s", action)

    def handle_exit(self):
        self.stop_event.set()
    
    def handle_commands(self):
        while True:
            try:
                action, params = self.command_queue.get_nowait()
                log.debug("action, params: %s, %s", action, params)
            except queue.Empty:
                return
            else:
                self.dispatch(action, params)

    def queue_command(self, action, params):
        """Normalise and queue a non-null command.
        """
        if action is None:
            return
        else:
            self.command_queue.put((action, params))
    
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
    
    def finish(self):
        self.stop_event.set()
    
    def finished(self):
        return self.stop_event.is_set()
    
    #
    # Main loop
    #
    def run(self):
        """Handle robot commands placed on the queue by the .generate_commands
        processor specific to this programme. 
        """
        while not self.finished():
            try:
                self.generate_commands()
                self.handle_commands()
            except KeyboardInterrupt:
                log.warn("Closing Controller gracefully...")
                self.stop_event.set()
            except:
                log.exception("Problem in Controller")
                self.stop_event.set()

