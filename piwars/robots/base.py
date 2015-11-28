# -*- coding: utf-8 -*-
import time
from ..core import config
from ..core import logging

class NEVER(object):
    
    def __bool__(self):
        return False
    
    def __float__(self):
        return 0.0

class BaseRobot(object):
    
    def __init__(self):
        pass
        
    def forward(self, speed=1, stop_after_secs=NEVER):
        pass
        
    def backward(self, speed=1, stop_after_secs=NEVER):
        pass
    back = backward
        
    def left(self, speed=1, stop_after_secs=NEVER):
        pass

    def right(self, speed=1, stop_after_secs=NEVER):
        pass
        
    def turn(direction, extent=1.0, speed=1.0, stop_after_secs=NEVER):
        pass

    def stop(self):
        pass
