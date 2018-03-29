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
        print('Failed to initialize all system components')
        sys.exit()
        
    # Main program loop
    while monitor.powerOn():                         # Loops while main power is on
        while monitor.doorClosed():                  # Loops while door is closed
            if monitor.checkTemp():                  # Check temperature
                monitor.tempWarning()
            
            if monitor.doorOpen():                   # If door is opened
                monitor.startTimer()                 # Start door timer
                
                while monitor.doorOpen():            # Loop while door remains open
                    if monitor.timerExceeded():      # Issue warning if timer exceeded
                        monitor.doorWarning()
                
                    if monitor.checkTemp():          # Continue checking temp since door is open
                        monitor.tempWarning()

                scale.getWeight()                    # Get weight on scale
                if scale.weight > 0:                 # If item was placed on scale
                    detect.getImage()                # Take picture of item
                    detect.detectLabels()            # Send image to Vision API
                    detect.parseRespsone()           # Match response with list of known items
                    storage.addItem(                 # Add item info to list
                        detect.item,
                        scale.weight,
                        detect.filename)
                elif scale.weight < 0:               # If item was removed
                    storage.removeItem(scale.weight) # Find it in datastore and remove
                else:
                    pass                             # No item placed on scale
            else:
                pass                                 # Continue looping if door remains closed     
        print('Door must be closed on monitor start') 
    else:
        monitor.powerWarning()                       # Issue power warning if power fails

# Call main()
if __name__ == '__main__':
    main()