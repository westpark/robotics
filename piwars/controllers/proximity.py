# -*- coding: utf-8 -*-
import os, sys
import collections
import itertools
import queue
import threading
import time

from ..core import config, exc, logging, utils
log = logging.logger(__package__)
from . import remote
from . import statistics34 as statistics
from ..sensors import ultrasonic

#
# This controller is trying to have the robot get as close as it can
# to a wall without swerving too far from side to side. Both sensors
# should be pointing forwards and we'll be detecting unwanted swerve
# by determining when they are offset from each other.
#

#
# How close is close enough?
#
PROXIMITY_THRESHOLD = 200

class Controller(remote.Controller):

    N_SAMPLES = 10
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started = False
        self.sensor_queues = {}
        self.sensor_threads = []
        self.distances = {}
        for position in ["right"]:
            sensor_name = "%s_ultrasonic" % position
            sensor_config = config.ini[sensor_name]
            trigger_pin = int(sensor_config['trigger_pin'])
            echo_pin = int(sensor_config['echo_pin'])
            log.info("Setting up %s on trigger %d and echo %d", sensor_name, trigger_pin, echo_pin)
            sensor = ultrasonic.Sensor(trigger_pin, echo_pin, sensor_name)
            q = self.sensor_queues[position] = queue.Queue()
            self.distances[position] = collections.deque([], self.N_SAMPLES)
            sensor_thread = threading.Thread(target=self.distance_sensor, args=(sensor, q))
            self.sensor_threads.append(sensor_thread)

    def dispatch(self, action, params):
        if not self.started and action not in ("start", "stop"):
            log.warn("Cannot dispatch %s : %s when not yet started", action, ", ".join(params))
        else:
           super().dispatch(action, params) 
    
    def distance_sensor(self, sensor, queue):
        log.info("About to enable sensor %s", sensor)
        sensor.steady_trigger()
        while not self.finished():
            distance = sensor.find_distance_mm()
            queue.put(distance)
    
    def handle_start(self):
        log.info("Starting up sensor threads")
        for sensor_thread in self.sensor_threads:
            sensor_thread.start()
        self.started = True
        
        #
        # Wait until we start to get readings from the
        # sensor before setting off
        #
        log.info("Waiting for first readings")
        while self.current_distance(self.distances['right']) is None:
            self.read_distances()
        
        log.info("Moving robot forward")
        self.robot.forward()
    
    def handle_stop(self):
        log.info("About to stop")
        self.robot.stop()
        self.started = False
        self.finish()

    def read_distances(self):
        """Add any new distance readings from the sensors
        """
        for position in self.sensor_queues:
            try:
                distance = self.sensor_queues[position].get_nowait()
            except queue.Empty:
                continue
            else:
                self.distances[position].append(distance)

    def current_distance(self, distances):
        """Discard any outliers and return the most recent reading
        for this sensor
        """
        robust_distances = utils.without_outliers(distances)
        if robust_distances:
            return robust_distances[-1]
        else:
            return None
    
    def generate_commands(self):
        #
        # Handle remote commands first
        #
        #~ super().generate_commands()
        #
        # Pick up the latest movements recorded from the lateral sensors
        #
        t0 = time.time()
        self.read_distances()
        distance = self.current_distance(self.distances['right'])

        log.debug("Current distance: %s", distance)
        #~ if time.time() - t0 > 5:
        if distance < PROXIMITY_THRESHOLD:
            log.info("Distance below proximity threshold; stopping")
            self.handle_stop()

    #
    # Main loop
    #
    def run(self):
        """Since we don't seem able to cope with remote commands
        followed by local control, always start without waiting for
        a remote instruction
        """
        self.handle_start()
        super().run()
