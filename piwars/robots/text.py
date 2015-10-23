# -*- coding: utf-8 -*-
import time

from ..core import config
from ..core import logging
from . import base

class Robot(base.BaseRobot):

    def forwards(self, left_or_right="both", stop_after_secs=base.NEVER):
        print("Moving %s forwards..." % left_or_right)
        if stop_after_secs is not base.NEVER:
            time.sleep(stop_after_secs)
            self.stop(left_or_right)

    def backwards(self, left_or_right="both", stop_after_secs=base.NEVER):
        print("Moving %s backwards..." % left_or_right)
        if stop_after_secs is not base.NEVER:
            time.sleep(stop_after_secs)
            self.stop(left_or_right)

    def stop(self, left_or_right="both"):
        print("Stopping %s..." % left_or_right)
