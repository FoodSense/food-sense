# foodSense.py
# DT08 - Food Sense
# c. 2018 Derrick Patterson and Mavroidis Mavroidis. All rights reserved.

from detect.detect import Detect
from scale.scale import Scale
from storage.storage import Storage
from system.system import System
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
    maxOpen = 120   # Max amount of time (in seconds) for door to remain open
    maxTemp = 4.4   # Max temperature in Celcius

    # Begin initializing necessary components
    try:
        system = System(DOOR, POWER)  # System monitoring
        scale = Scale(DATA, CLK)      # HX711 for reading scale    
        detect = Detect(LED)          # Camera, Vision API, and parsing
        storage = Storage()           # Cloud Datastore interface

    except AttributeError:
        print('Failed to initialize all system components')
        sys.exit()
        
    # Main program loop
    while system.powerOn():
        while system.doorClosed():

            if system.checkTemp():
                system.tempWarning()

            if system.doorOpen():
                system.startTimer()
                while system.doorOpen():  

                    if system.checkTemp():
                        system.tempWarning()

                    if system.timerExceeded():
                        system.doorWarning()
                scale.getWeight()
                
                if scale.weight > 0:
                    detect.getImage()
                    detect.detectLabels()
                    detect.parseRespsone()
                    storage.addItem(detect.item, scale.weight, detect.filename)
                elif scale.weight < 0:
                    storage.removeItem(scale.weight)
                else:
                    print('Error: no weight detected on scale')
            else:
                pass     
        print('Door must be closed on system start') 
    system.powerWarning()
    sys.exit()

# Call main()
if __name__ == '__main__':
    main()