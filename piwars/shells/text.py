#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
import shlex

from . import comms

def start():
    sender = comms.Sender()
    while True:
        command = input("Command: ")
        response = sender.send(command)
        print("  ... %s" % response)
        words = shlex.split(response.lower())
        status = words[0]
        if len(words) > 1:
            info = words[1:]

if __name__ == '__main__':
    start(*sys.argv[1:])
