# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from ..core import config
from ..core import logging

NEVER = object()

class BaseRobot(object):
    
    def __init__(self):
        pass

    def move(self, forwards_or_backwards, left_or_right, stop_after_secs=NEVER):
        assert forwards_or_backwards in ("forward", "backwards")
        assert left_or_right in ("left", "right")

    def forwards(self, stop_after_secs=NEVER):
        raise NotImplementedError

    def backwards(self, stop_after_secs=NEVER):
        raise NotImplementedError

    def left(self, stop_after_secs=NEVER):
        raise NotImplementedError

    def right(self, stop_after_secs=NEVER):
        raise NotImplementedError

    def stop(self, stop_after_secs=NEVER):
        raise NotImplementedError
