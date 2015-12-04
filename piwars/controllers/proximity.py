# -*- coding: utf-8 -*-
import os, sys
import collections
import itertools
import queue
import threading

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
# How much difference does there have to be between one
# sensor and the other to constitute a swerve?
#
OFFSET_THRESHOLD = 10
PROXIMITY_THRESHOLD = 45

TRIGGER_PIN = 3
ECHO_PIN = 4

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
            sensor = ultrasonic.Sensor(sensor_config['trigger_pin'], sensor_config['echo_pin'], "ultrasonic")
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
        sensor.steady_trigger()
        while not self.finished():
            distance = sensor.find_distance_mm()
            queue.put(distance)
    
    def handle_start(self):
        for sensor_thread in self.sensor_threads:
            sensor_thread.start()
        self.started = True
        
        self.robot.forward()
    
    def handle_stop(self):
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
            return PROXIMITY_THRESHOLD + 1
    
    def effective_offset(self):
        left_distance = current_distance(self.distances["left"])
        right_distance = current_distance(self.distances["right"])
        return left_distance - right_distance            
    
    def generate_commands(self):
        #
        # Handle remote commands first
        #
        #~ super().generate_commands()
        #
        # Pick up the latest movements recorded from the lateral sensors
        #
        self.read_distances()
        distance = self.current_distance(self.distances['right'])
        print("Distance:", distance)
        if distance < PROXIMITY_THRESHOLD:
            self.handle_stop()

    #
    # Main loop
    #
    def run(self):
        """Handle robot commands placed on the queue by the .generate_commands
        processor specific to this programme. 
        """
        self.handle_start()
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
