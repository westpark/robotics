# -*- coding: utf-8 -*-
import time

from ..core import config
from ..core import logging
from . import base

class Robot(base.BaseRobot):

    def forward(self, *args):
        print("forward", args)

    def backward(self, *args):
        print("backward", args)

    def left(self, *args):
        print("left", args)

    def right(self, *args):
        print("right", args)

    def stop(self, *args):
        print("stop", args)
