# foodSense.py
# DT08 - Food Sense
# c. 2018 Derrick Patterson and Mavroidis Mavroidis. All rights reserved.

from detect import Detect
from scale import Scale
from storage import Storage
from monitor import Monitor
import sys

# Main method
def main():
    print('Starting Food Sense')
    
    CLK = 17        # HX711 clk pin
    DATA = 22       # HX711 data pin
    DOOR = 27       # Door monitoring pin
    LED = 5         # LED power pin
    POWER = 26      # Power monitoring pin

    # Begin initializing necessary components
    print('Initializing monitor components')
    try:
        monitor = Monitor(DOOR, POWER)  # System monitoring
        scale = Scale(DATA, CLK)        # HX711 for reading scale    
        detect = Detect(LED)            # Camera, Vision API, and parsing
        storage = Storage()             # Cloud Datastore interface

    except AttributeError:
        print('Failed to initialize all monitor components')
        sys.exit()
        
    # Main program loop
    while monitor.powerOn():
        while monitor.doorClosed():
            if monitor.checkTemp():
                monitor.tempWarning()
            
            if monitor.doorOpen():
                monitor.startTimer()
                
                while monitor.doorOpen():      
                    if monitor.timerExceeded():
                        monitor.doorWarning()
                
                    if monitor.checkTemp():
                        monitor.tempWarning()

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
        print('Door must be closed on monitor start') 
    monitor.powerWarning()
    sys.exit()

# Call main()
if __name__ == '__main__':
    main()