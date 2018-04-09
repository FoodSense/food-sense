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

# Entrypoint
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
        #detect = Detect(LED)
        storage = Storage()
        #monitor = Monitor(DOOR, POWER)
        #scale = Scale(DATA, CLK)
    except AttributeError:
        print('Failed to initialize all system components')
        sys.exit()

    ### START DEBUG ###

    storage.doorWarning()

    ### END DEBUG ###

    # Main program loop
#    while True:
#        while monitor.powerOn():
#            while monitor.doorClosed():
#                if monitor.checkTemp():
#                    storage.tempWarning()
#                if monitor.doorOpen():
#                    monitor.startTimer()
#                    
#                    while monitor.doorOpen():
#                        if monitor.timerExceeded():
#                            storage.doorWarning()
#                        if monitor.checkTemp():
#                            storage.tempWarning()
#                    scale.getWeight()
                    
#                    if scale.weight > 0:
#                        detect.getImage()
#                        detect.detectItem()
#                        detect.parseResponse()
#                        storage.addItem(
#                                detect.item,
#                                scale.weight, 
#                                detect.timestamp)
#                        storage.uploadImage(detect.timestamp, detect.filename)
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
