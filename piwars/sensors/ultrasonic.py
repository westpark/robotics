#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
import atexit

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
atexit.register(GPIO.cleanup)

import time

from ..core import config
from ..core import logging

THRESHOLD_MM = 10
THRESHOLD_SECS = 0.1
SPEED_OF_SOUND = 343 * 100 * 10 # mm/s
TOLERANCE_MM = 30

class Sensor(object):
    
    def __init__(self, trigger_pin, echo_pin, name):
        self.name = name
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.initialise_pins()
        self.steady_trigger()

    def initialise_pins(self):
        """Intialise the GPIO pins we're using
        
        Set up the trigger pin as an output and the echo
        pin as an input
        """
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def steady_trigger(self):
        """Steady the trigger mechanism
        
        The sensor needs the trigger line to be low for a short period
        before actually starting to operate. We're waiting for two seconds
        but it's pretty much arbitrary
        """
        GPIO.output(self.trigger_pin, False)
        time.sleep(2)

    def pulse_trigger(self):
        """Pulse the trigger line
        
        Set the trigger line high for a millisecond. This is what the
        sensor is expecting to initiate a reading.
        """
        GPIO.output(self.trigger_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, False)

    def wait_for_echo(self):
        """Wait for the echo return from the sensor
        
        Once the trigger line is pulsed, the sensor sends out a sound
        wave and waits for it to bounce back from a nearby object. To
        indicate back to us how long that bounce took, the sensor sets
        the echo line high for the same amount of time as it waited
        for the bounce to return.
        """
        
        #
        # Wait for the echo line to go high
        #
        t0 = start = time.time()
        while GPIO.input(self.echo_pin) == 0:
            start = time.time()
            if start - t0 > THRESHOLD_SECS:
                print("Waited for more than %s seconds" % THRESHOLD_SECS)
                return start - t0
        #
        # Now start the clock and wait for it to go low again
        #
        end = start
        while GPIO.input(self.echo_pin) == 1:        
            end = time.time()
            if end - start > THRESHOLD_SECS:
                return end - start
        
        #
        # The difference between the two timestamps is the number
        # of seconds the bounce took to return to the sensor.
        #
        return end - start

    def convert_delay_to_distance(self, delay_secs):
        """Convert the number of seconds delay into a distance from an object
        
        The number of seconds represents the time it took a sound wave
        to travel to a nearby object and back. We know the speed of sound
        (in mm/s in our case). We obtain the distance by multiplying the
        time taken by the speed. This gives us the distance in mm *both there
        and back*. To obtain the distance, we divide this distance by 2.
        """
        total_distance = delay_secs * SPEED_OF_SOUND 
        outbound_distance_mm = total_distance / 2
        adjusted_distance_mm =  outbound_distance_mm - TOLERANCE_MM
        return adjusted_distance_mm

    def find_distance_mm(self):
        """Find the distance in mm to a nearby object
        
        Pulse the trigger, wait for the delay to be signalled
        on the echo line, and calculate the distance in mm.
        """
        self.pulse_trigger()
        delay_secs = self.wait_for_echo()
        #print("Delay: %3.6f" % delay_secs)
        return self.convert_delay_to_distance(delay_secs)

if __name__ == '__main__':
    sensor1 = Sensor(23, 24, "Right")
    sensor2 = Sensor(15, 18,"Left")
    sensors = [sensor1, sensor2]
    for sensor in sensors:
        sensor.initialise_GPIO()
        sensor.initialise_pins()
        sensor.steady_trigger()
    
    while True:
        for s in sensors:
            distance_mm = s.find_distance_mm()
            print(s.name, "%5.2fmm" % distance_mm)
            if distance_mm < THRESHOLD_MM:
                print ("stop")
                break
        time.sleep(0.1)
