# -*- coding: utf-8 -*-
import time

from ..core import config
from ..core import logging
from . import base
from . import robot

NEVER = base.NEVER

class Robot(base.BaseRobot):
    
    def __init__(self):
        super().__init__()
        self.robot = robot.Robot()

    def forward(self, speed=1, stop_after_secs=NEVER):
        self.robot.forward(float(speed))
        self.stop(stop_after_secs)
        
    def backward(self, speed=1, stop_after_secs=NEVER):
        self.robot.backward(float(speed))
        self.stop(stop_after_secs)
    back = backward
        
    def left(self, speed=1, stop_after_secs=NEVER):
        self.robot.left(float(speed))
        self.stop(stop_after_secs)

    def right(self, speed=1, stop_after_secs=NEVER):
        self.robot.right(float(speed))
        self.stop(stop_after_secs)

    def turn(self, direction, extent=1.0, speed=1.0, stop_after_secs=NEVER):
        self.robot.turn(direction, float(extent), float(speed))
        self.stop(stop_after_secs)
        
    def stop(self, delay_secs=0):
        if delay_secs is NEVER:
            return
        else:
            time.sleep(float(delay_secs))
            self.robot.stop()