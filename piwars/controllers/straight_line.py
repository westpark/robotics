# -*- coding: utf-8 -*-
import os, sys

from ..core import config, exc, logging
from . import remote
log = logging.logger(__package__)

class Controller(remote.Controller):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.started = False

    def dispatch(self, action, params):
        if not self.started and action not in ("start", "stop"):
            log.warn("Cannot dispatch %s : %s when not yet started", action, ", ".join(params))
        else:
           super().dispatch(action, params) 
    
    def handle_start(self):
        self.started = True
    
    def handle_stop(self):
        self.robot.stop()
        self.started = False
    
    def generate_commands(self):
        #
        # Handle remote commands first
        #
        super().generate_commands()
