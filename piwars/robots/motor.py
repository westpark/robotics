# -*- coding: utf-8 -*-
import time

from ..core import config
from ..core import logging
from . import base
from . import drive0

class Robot(base.BaseRobot):


    def forward(self, speed=1):
        speed=float(speed)
        print('forward', speed)
        drive0.robot.forward(speed)
        
    def backward(self, speed=1):
        speed=float(speed)
        print('backward', speed)
        drive0.robot.backward(speed)
        
    def left(self, speed=1):
        speed=float(speed)
        print('left', speed)
        drive0.robot.left(speed)

    def right(self, speed=1):
        speed=float(speed)
        print('right', speed)
        drive0.robot.right(speed)
        
    def stop(self):
        print('stop')
        drive0.robot.stop()