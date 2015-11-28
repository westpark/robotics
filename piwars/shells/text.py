# -*- coding: utf-8 -*-
import os, sys
import cmd
import shlex

from ..core import comms

class Shell(cmd.Cmd):

    prompt = ">>> "
    
    def __init__(self):
        super().__init__()
        self.sender = comms.Sender()
    
    def command(self, command):
        print(self.sender.send(command))
    
    def do_start(self, arg):
        return self.command("start")
    
    def do_stop(self, arg):
        "Stop the robot"
        return self.command("stop")
    
    def do_forward(self, arg):
        "Go forward: [speed] [stop_after_secs]"
        return self.command("forward %s" % arg)
        
    def do_backward(self, arg):
        "Go backward: [speed] [stop_after_secs]"
        return self.command("backward %s" % arg)
    
    def do_left(self, arg):
        "Go left: [speed] [stop_after_secs]"
        return self.command("left %s" % arg)

    def do_right(self, arg):
        "Go right: [speed] [stop_after_secs]"
        return self.command("right %s" % arg)
    
    def do_turn(self, arg):
        "Turn [left|right] [extent] [speed] [stop_after_secs]" 
        return self.command("turn %s" % arg)
    
    def default(self, line):
        return self.command(line)        

    def start(self):
        return self.cmdloop()

