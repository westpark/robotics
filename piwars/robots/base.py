# -*- coding: utf-8 -*-
from ..core import config
from ..core import logging

NEVER = object()

class BaseRobot(object):
    
    def __init__(self):
        pass

    def move(self, forwards_or_backwards, left_or_right="both", stop_after_secs=NEVER):
        if forwards_or_backwards == "forwards":
            return self.forwards(left_or_right, stop_after_secs)
        elif forwards_or_backwards == "backwards":
            return self.backwards(left_or_right, stop_after_secs)
        else:
            raise RuntimeError("No such direction: %s" % forwards_or_backwards)
            
    def forwards(self, left_or_right="both", stop_after_secs=NEVER):
        raise NotImplementedError

    def backwards(self, left_or_right="both", stop_after_secs=NEVER):
        raise NotImplementedError

    def stop(self, left_or_right="both"):
        raise NotImplementedError
