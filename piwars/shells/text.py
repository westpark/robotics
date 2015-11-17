# -*- coding: utf-8 -*-
import os, sys
import shlex

from .core import comms

class Shell(object):

    def start(self):
        sender = comms.Sender()
        while True:
            command = input("Command: ")
            response = sender.send(command)
            print("  ... %s" % response)
            words = shlex.split(response.lower())
            status = words[0]
            if len(words) > 1:
                info = words[1:]
