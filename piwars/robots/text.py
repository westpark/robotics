# -*- coding: utf-8 -*-
import time

from ..core import config
from ..core import logging
from . import base

class Robot(base.BaseRobot):

    def _forwards(self, left_or_right="both", stop_after_secs=base.NEVER):
        print("Moving %s forwards..." % left_or_right)

    def _backwards(self, left_or_right="both", stop_after_secs=base.NEVER):
        print("Moving %s backwards..." % left_or_right)
    
    def stop(self, left_or_right="both"):
        print("Stopping %s..." % left_or_right)
