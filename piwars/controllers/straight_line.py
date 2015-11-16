# -*- coding: utf-8 -*-
import os, sys
import collections
import queue
import threading

from ..core import config, exc, logging
log = logging.logger(__package__)
from . import remote
from ..sensors import ultrasonic

class Controller(remote.Controller):

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
            self.distances[position] = deque.deque([], 10)
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
        for position in "left", "right":
            try:
                distance = self.sensor_queues[position].get_nowait()
            except queue.Empty:
                continue
            else:
                self.distances[position].append(distance)
    
    def generate_commands(self):
        #
        # Handle remote commands first
        #
        super().generate_commands()
        #
        # Attempt to detect a lateral movement and compensate
        #
        self.read_distances()
