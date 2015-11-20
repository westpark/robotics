# -*- coding: utf-8 -*-
import os, sys
import collections
import itertools
import queue
import statistics
import threading

from ..core import config, exc, logging, utils
log = logging.logger(__package__)
from . import remote
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
PROXIMITY_THRESHOLD = 30

class Controller(remote.Controller):

    N_SAMPLES = 10
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started = False
        self.sensor_queues = {}
        self.sensor_threads = []
        self.distances = {}

    def dispatch(self, action, params):
        if not self.started and action not in ("start", "stop"):
            log.warn("Cannot dispatch %s : %s when not yet started", action, ", ".join(params))
        else:
           super().dispatch(action, params) 
    
    def distance_sensor(self, sensor, queue):
        sensor.steady_trigger()
        while not self.finished():
            queue.put(sensor.find_distance_mm())
    
    def handle_start(self):
        for position in "left", "right":
            sensor_name = "%s_ultrasonic" % position
            sensor_config = config[sensor_name]
            sensor = ultrasonic.Sensor(sensor_config.trigger_pin, sensor_config.echo_pin)
            queue = self.sensor_queues[position] = queue.Queue()
            self.distances[position] = deque.deque([], self.N_SAMPLES)
            sensor_thread = threading.Thread(target=self.distance_sensor, args=(sensor, queue))
            self.sensor_threads.append(sensor_thread)
            
        for sensor_thread in self.sensor_threads:
            thread.start()
        self.started = True
        
        self.robot.forward()
    
    def handle_stop(self):
        self.robot.stop()
        self.started = False

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
        robust_distances utils.without_outliers(distances)
        return robust_distances[-1]
    
    def effective_offset(self):
        left_distance current_distance(self.distances["left"])
        right_distance = current_distance(self.distances["right"])
        return left_distance - right_distance            
    
    def generate_commands(self):
        #
        # Handle remote commands first
        #
        super().generate_commands()
        #
        # Pick up the latest movements recorded from the lateral sensors
        #
        self.read_distances()
        #
        # If either distance is within the proximity threshold, stop
        # Otherwise, if the difference between the two is greater than
        # the offset threshold, swerve the other way
        #
        left_distance = current_distance(self.distances["left"])
        right_distance = current_distance(self.distances["right"])
        if left_distance < PROXIMITY_THRESHOLD or right_distance < PROXIMITY_THRESHOLD:
            self.handle_stop()
        elif left_distance - right_distance > OFFSET_THRESHOLD:
            self.robot.turn("right")
        elif right_distance - left_distance > OFFSET_THRESHOLD:
            self.robot.turn("left")
