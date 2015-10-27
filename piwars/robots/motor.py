# -*- coding: utf-8 -*-
import time

from gpiozero import Robot

from ..core import config
from ..core import logging
from . import base

class Robot(base.BaseRobot):
    
    def __init__(self):
        super().__init__(self)
        self.robot = Robot(left=(17, 18), right=(23, 22))

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
        
    def stop(self):
        print('stop')
        self.robot.stop()