# -*- coding: utf-8 -*-
import time

from ..core import config
from ..core import logging
log = logging.logger(__package__)

class Never(object):
    
    def __repr__(self):
        return "<Never>"

NEVER = Never()

class BaseRobot(object):

    def _validate_left_or_right(self, left_or_right):
        assert left_or_right.strip().lower() in ("left", "right", "both")

    def move(self, forwards_or_backwards, left_or_right="both", stop_after_secs=NEVER):
        log.debug("Move %s %s until %s secs", left_or_right, forwards_or_backwards, stop_after_secs)
        if forwards_or_backwards == "forwards":
            return self.forwards(left_or_right, stop_after_secs)
        elif forwards_or_backwards == "backwards":
            return self.backwards(left_or_right, stop_after_secs)
        else:
            raise RuntimeError("No such direction: %s" % forwards_or_backwards)
            
    def forwards(self, left_or_right="both", stop_after_secs=NEVER):
        log.debug("Forwards %s until %s secs", left_or_right, stop_after_secs)
        self._validate_left_or_right(left_or_right)
        self._forwards(left_or_right)
        if stop_after_secs is not NEVER:
            time.sleep(float(stop_after_secs))
            self.stop(left_or_right)

    def backwards(self, left_or_right="both", stop_after_secs=NEVER):
        log.debug("Backwards %s until %s secs", left_or_right, stop_after_secs)
        self._validate_left_or_right(left_or_right)
        self._backwards(left_or_right)
        if stop_after_secs is not NEVER:
            time.sleep(float(stop_after_secs))
            self.stop(left_or_right)

    def stop(self, left_or_right="both"):
        log.debug("Stop", left_or_right)
        self._validate_left_or_right(left_or_right)
        self._stop(left_or_right)
