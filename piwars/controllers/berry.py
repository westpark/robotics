# -*- coding: utf-8 -*-
import os, sys
import collections
import itertools
import queue
import threading
import time

import pyberryimu.client

from ..core import config, exc, logging, utils
log = logging.logger(__package__)
from . import remote

#
# This controller is trying to have the robot get as close as it can
# to a wall without swerving too far from side to side. Both sensors
# should be pointing forwards and we'll be detecting unwanted swerve
# by determining when they are offset from each other.
#

#
# How much difference does there have to be between one
# sensor and the other to constitute a swerve?
#
OFFSET_THRESHOLD = 10
PROXIMITY_THRESHOLD = 30

class Controller(remote.Controller):

    N_SAMPLES = 100
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started = False
        self.queues = {
            "acc" : queue.Queue(),
            "gyro" : queue.Queue(),
            "mag" : queue.Queue()
        }

    def dispatch(self, action, params):
        if not self.started and action not in ("start", "stop", "exit"):
            log.warn("Cannot dispatch %s : %s when not yet started", action, ", ".join(params))
        else:
           super().dispatch(action, params) 

    def read_berry(self, name, q, function):
        while not self.finished():
            t, v = time.time(), function()
            q.put((t, v))
            time.sleep(0.05)
    
    def handle_start(self):
        berry = pyberryimu.client.BerryIMUClient(bus=1)
        threading.Thread(target=self.read_berry, args=("acc", self.queues['acc'], berry.read_accelerometer)).start()
        threading.Thread(target=self.read_berry, args=("gyro", self.queues['gyro'], berry.read_gyroscope)).start()
        threading.Thread(target=self.read_berry, args=("mag", self.queues['mag'], berry.read_magnetometer)).start()
        
        self.started = True        
        self.robot.forward()
    
    def handle_stop(self):
        self.finish()
        self.robot.stop()
        self.started = False

    def get_reading(self, q):
        try:
            return q.get_nowait()
        except queue.Empty:
            return None, None
    
    def get_berry_readings(self):
        """Add any new readings from the berry
        """
        for type, q in self.queues.items():
            t, v = self.get_reading(q)
            if t:
                print(type, "=>", v)
    
    def generate_commands(self):
        #
        # Handle remote commands first
        #
        super().generate_commands()
        #
        # Pick up the latest movements recorded from the sensors
        #
        self.get_berry_readings()
