#!/usr/bin/python3
import sys
import time
import RPi.GPIO as GPIO
from scale import Scale

DATA = 22
SCK = 17

scale = Scale(22, 17)

scale.setReferenceUnit(21)

scale.reset()
scale.tare()

while True:

    try:
        #scale.getWeight()
        #print("{0: 4.4f}".format(scale.weight))
        val = scale.getMeasure()
        print("{0: 4.4f}".format(val))
        time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        GPIO.cleanup()
        sys.exit()