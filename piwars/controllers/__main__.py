#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import importlib

from .. import robots

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller", default="remote")
    parser.add_argument("--robot", default="text")
    args = parser.parse_args()
    
    try:
        module = importlib.import_module(".%s" % args.robot, "piwars.robots")
    except ImportError:
        raise RuntimeError("Invalid robot: %s" % args.robot)
    else:
        robot = module.Robot()

    try:
        module = importlib.import_module(".%s" % args.controller, "piwars.controllers")
    except ImportError:
        raise RuntimeError("Invalid controller: %s" % args.controller)
    else:
        controller = module.Controller(robot)
    
    controller.run()
