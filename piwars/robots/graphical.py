# -*- coding: utf-8 -*-
import queue
import threading
import turtle

import pygame
from pygame.locals import *

from ..core import config
from ..core import logging
from . import base

class ThreadingTurtle(threading.Thread):
    
    speed = 1 ## pixel per frame
    
    def __init__(self, command_queue):
        self.queue = command_queue
    
    

class Robot(base.BaseRobot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        turtle.setpos((0, 0))

    def _forwards(self, left_or_right="both"):
        
        print("Moving %s forwards..." % left_or_right)

    def _backwards(self, left_or_right="both"):
        print("Moving %s backwards..." % left_or_right)

    def stop(self, left_or_right="both"):
        print("Stopping %s..." % left_or_right)
