# -*- coding: utf-8 -*-
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
        if stop_after_secs is not NEVER:
            time.sleep(float(stop_after_secs))
            self.robot.stop()
        
    def backward(self, speed=1, stop_after_secs=NEVER):
        self.robot.backward(float(speed))
        if stop_after_secs is not NEVER:
            time.sleep(float(stop_after_secs))
            self.robot.stop()
        
    def left(self, speed=1, stop_after_secs=NEVER):
        self.robot.left(float(speed))
        if stop_after_secs is not NEVER:
            time.sleep(float(stop_after_secs))
            self.robot.stop()

    def right(self, speed=1, stop_after_secs=NEVER):
        self.robot.right(float(speed))
        if stop_after_secs is not NEVER:
            time.sleep(float(stop_after_secs))
            self.robot.stop()

    def turn(self, direction, extent=1.0, speed=1.0, stop_after_secs=NEVER):
        self.robot.turn(direction, float(extent), float(speed))
        if stop_after_secs is not NEVER:
            time.sleep(float(stop_after_secs))
            self.robot.stop()
        
    def stop(self):
        self.robot.stop()