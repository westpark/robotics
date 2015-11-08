# -*- coding: utf-8 -*-
import gpiozero

class Robot(gpiozero.Robot):

    def __init__(self):
        super().__init__(left=(17, 18), right=(23, 22))
    
    def turn(self, direction, extent=1.0, speed=1.0):
        if direction == "left":
            self._left.forward(speed * extent)
            self._right.forward(speed * (1.0 - extent))
        elif direction == "right":
            self._right.forward(speed * extent)
            self._left.forward(speed * (1.0 - extent))
        else:
            raise RuntimeError("No such direction: %s" % direction)
