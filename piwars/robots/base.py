# -*- coding: utf-8 -*-
from ..core import config
from ..core import logging

NEVER = object()

class BaseRobot(object):
    
    def __init__(self):
        pass
        
    def forward(self, speed=1):
        print('forwards')
        speed=float(speed)
        
    def backward(self, speed=1):
        print('backwards')
        speed=float(speed)
        
    def left(self, speed=1):
        print('left')
        speed=float(speed)

    def right(self, speed=1):
        print('right')
        speed=float(speed)
        
    def turn(direction, extent):
        raise NotImplementedError

    def stop(self):
        print('stop')
        
