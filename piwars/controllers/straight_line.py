# -*- coding: utf-8 -*-
import os, sys
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
        self.left_ultrasonic = ultrasonic.Sensor(
            config['left_ultrasonic'].trigger_pin, 
            config['left_ultrasonic'].echo_pin
        ) 
        self.right_ultrasonic = ultrasonic.Sensor(
            config['right_ultrasonic'].trigger_pin, 
            config['right_ultrasonic'].echo_pin
        )
        self.sensor_queues = {}
        self.sensor_threads = []

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
            queue = self.sensor_queues[sensor_name] = queue.Queue()
            self.sensor_threads.append(threading.Thread(target=self.distance_sensor, args=(sensor, queue)))
            
        for thread in self.sensor_threads:
            thread.start()
        self.started = True
    
    def handle_stop(self):
        self.robot.stop()
        self.started = False
    
    def generate_commands(self):
        #
        # Handle remote commands first
        #
        super().generate_commands()
