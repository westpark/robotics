#!/usr/bin/env python3
import os, sys
import cmd

class C(cmd.Cmd):
    
    def do_hello(self, *args):
        print("Hello", args)
    
    def do_bye(self, *args):
        print("Bye")
        return True

C().cmdloop()

