# foodSense.py
# DT08 - Food Sense
# c. 2018 Derrick Patterson and Mavroidis Mavroidis. All rights reserved.

from detect import Detect
from monitor import Monitor
from scale import Scale
from storage import Storage
import RPi.GPIO as GPIO
import sys
import time

# Main method
def main():
    print('Starting Food Sense')
    
    CLK = 17        # HX711 clk pin
    DATA = 22       # HX711 data pin
    DOOR = 27       # Door monitoring pin
    LED = 5         # LED power pin
    POWER = 26      # Power monitoring pin
    GPIO.setmode(GPIO.BCM)

    # Begin initializing necessary components
    print('Initializing system components')
    try:
        #monitor = Monitor(DOOR, POWER)  # System monitoring
        scale = Scale(DATA, CLK)        # HX711 for reading scale    
        detect = Detect(LED)            # Camera, Vision API, and parsing
        storage = Storage()               # storage interface
    except AttributeError:
        print('Failed to initialize all system components')
        sys.exit()
        
    # Main program loop
    while True:# monitor.powerOn():                         # Loops while main power is on
        while True:#monitor.doorClosed():                  # Loops while door is closed
            #if monitor.checkTemp():                  # Check temperature
            #    monitor.tempWarning()
            if True:#monitor.doorOpen():                   # If door is opened
                #monitor.startTimer()                 # Start door timer
                #while monitor.doorOpen():            # Loop while door remains open
                    #if monitor.timerExceeded():      # Issue warning if timer exceeded
                    #    monitor.doorWarning()
                    #if monitor.checkTemp():          # Continue checking temp since door is open
                    #    monitor.tempWarning()
                #scale.getWeight()                    # Get weight on scale
                scale.weight = 50
                if scale.weight > 0:                  # If item was placed on scale
                    #detect.getImage()
                    detect.filename = 'data/images/test.png'
                    #detect.timestamp = 'test'
                    #detect.detectItem()
                    #detect.parseResponse()
                    #storage.addItem(
                    #       detect.item,
                    #       scale.weight, 
                    #       detect.timestamp)
                    storage.uploadImage(detect.filename)
                elif scale.weight < 0:
                    storage.removeItem(scale.weight) # Find it in datastore and remove
                else:
                    pass                             # No item placed on scale
                sys.exit()
            else:
                pass
        else:
            print('Door must be closed on monitor start') 
    else:
        monitor.powerWarning()                       # Issue power warning if power fails

# Call main()
if __name__ == '__main__':
    main()
