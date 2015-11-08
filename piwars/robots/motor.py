# -*- coding: utf-8 -*-
from ..core import config
from ..core import logging
from . import base
from . import robot

class Robot(base.BaseRobot):
    
    def __init__(self):
        super().__init__()
        self.robot = robot.Robot()

    def forward(self, speed=1):
        speed=float(speed)
        print('forward', speed)
        self.robot.forward(speed)
        
    def backward(self, speed=1):
        speed=float(speed)
        print('backward', speed)
        self.robot.backward(speed)
        
    def left(self, speed=1):
        speed=float(speed)
        print('left', speed)
        self.robot.left(speed)

    def right(self, speed=1):
        speed=float(speed)
        print('right', speed)
        self.robot.right(speed)

    def turn(self, direction, extent=1.0, speed=1.0):
        extent = float(extent)
        speed = float(speed)
        print("turn", direction, extent, speed)
        self.robot.turn(direction, extent, speed)
        
    def stop(self):
        print('stop')
        self.robot.stop()