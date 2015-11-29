# -*- coding: utf-8 -*-
import os, sys
import collections
import itertools
import queue
import threading
import time

from ..core import config, exc, logging
log = logging.logger(__package__)
from . import remote
from ..sensors import ultrasonic

class Controller(remote.Controller):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started = False

    def dispatch(self, action, params):
        if not self.started and action not in ("start", "stop"):
            log.warn("Cannot dispatch %s : %s when not yet started", action, ", ".join(params))
        else:
           super().dispatch(action, params) 

    def drive(self):
        self.robot.forward(stop_after_secs=4)
        time.sleep(1)
        self.robot.turn(direction="left", extent=0.33, speed=1, stop_after_secs=4)        
        time.sleep(1)
        self.robot.backward(stop_after_secs=2.0)
        time.sleep(1)
        self.robot.turn(direction="left", extent=0.33, speed=1, stop_after_secs=4)        
        time.sleep(1)
        self.robot.forward(stop_after_secs=3.0)
        sys.exit()

    def handle_start(self):
        self.started = True
        self.drive()
    
    def handle_stop(self):
        self.robot.stop()
        self.started = False
