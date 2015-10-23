#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

from .. import robots
from . import controllers

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller", default="remote")
    parser.add_argument("--robot", default="text")
    args = parser.parse_args()
    
    if not hasattr(robots, args.robot):
        raise RuntimeError("Invalid robot: %s" % args.robot)
    else:
        module = getattr(robots, args.robot)
        robot = module.Robot()

    if args.controller not in controllers:
        raise RuntimeError("Invalid controller: %s" % args.controller)
    else:
        controller = controllers[args.controller]
    
    robot_controller = controller(robot=robot)
    robot_controller.start()
