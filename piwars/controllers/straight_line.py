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
        for position in self.sensor_queues:
            try:
                distance = self.sensor_queues[position].get_nowait()
            except queue.Empty:
                continue
            else:
                self.distances[position].append(distance)

    def movement(self, distances):
        robust_distances = utils.without_outliers(distances)
        #
        # Determine the overall movement over the last N_SAMPLES. If this is negative, we're
        # moving closer to that side; if positive, we're moving away.
        #
        return sum(b - a for (a, b) in zip(robust_distances[:-1], robust_distances[1:]))
    
    def effective_movement(self):
        left_movement = self.movement(self.distances["left"])
        right_movement = self.movement(self.distances["right"])
        if left_movement > right_movement:
            return "left":
        else:
            return "right"
    
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
        # Determine whether we need to move
        #
        effective_movement = self.effective_movement()
        if effective_movement == "left":
            self.robot.turn("right")
        elif effective_movement == "right":
            self.robot.turn("left")
