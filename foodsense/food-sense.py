# foodSense.py
# DT08 - Food Sense
# c. 2018 Derrick Patterson and Mavroidis Mavroidis. All rights reserved.

import sys
import time

try:
    #from detect import Detect
    #from monitor import Monitor
    #from scale import Scale
    from storage import Storage
except ImportError:
    print('Failed to import required Food Sense modules')
    sys.exit()

# Main method
def main():
    print('Starting Food Sense')

    # GPIO pins
    CLK = 17
    DATA = 22
    DOOR = 27
    LED = 5
    POWER = 26

    # Begin initializing necessary components
    print('Initializing system components')
    try:
        #monitor = Monitor(DOOR, POWER)
        #scale = Scale(DATA, CLK)
        #detect = Detect(LED)
        storage = Storage()
    except AttributeError:
        print('Failed to initialize all system components')
        sys.exit()

    storage.printList()
    storage.findByDTS('12345')
    storage.findByDTS('67890')
    storage.findByDTS('28734')

    #storage.findByWeight(50)
    #storage.findByWeight(100)
    sys.exit()

    # Main program loop
#    while True:
#        while monitor.powerOn():
#            while monitor.doorClosed():
#                if monitor.checkTemp():
#                    monitor.tempWarning()
#                if monitor.doorOpen():
#                    monitor.startTimer()
#                    
#                    while monitor.doorOpen():
#                        if monitor.timerExceeded():
#                            monitor.doorWarning()
#                        if monitor.checkTemp():
#                            monitor.tempWarning()
#                    scale.getWeight()
                    
#                    if scale.weight > 0:
#                        detect.getImage()
#                        detect.detectItem()
#                        detect.parseResponse()
#                        storage.addItem(
#                                detect.item,
#                                scale.weight, 
#                                detect.timestamp)
#                        storage.uploadImage(detect.filename)
#                    elif scale.weight < 0:
#                        storage.removeItem(scale.weight) 
#                    else:
#                        pass
#                    sys.exit()
#                else:
#                    pass
#            else:
#                print('Door must be closed on monitor start')
#        else:
#            monitor.powerWarning()
#    else:
#        pass

# Call main()
if __name__ == '__main__':
    main()
