# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import argparse

from .. import robots
from . import controller

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--robot", default="text")
    args = parser.parse_args()
    if not hasattr(robots, args.robot):
        raise RuntimeError("Invalid robot: %s" % args.robot)
    else:
        robot = getattr(robots, args.robot)
    
    robot_controller = controller.Controller(robot=robot)
    robot_controller.start()
