import sys
import time

try:
    #from monitor import Monitor
    #from scale import Scale
    from storage import Storage 
    from detect import Detect
except ImportError:
    print('Failed to import required Food Sense modules')
    sys.exit()

# Entrypoint
def main():
    print('Starting Food Sense')

    # GPIO pins
    CLK = 17
    DATA = 22
    DOOR = 5
    LED = 27
    POWER = 6

    # Begin initializing necessary components
    print('Initializing system components')
    try:
        #monitor = Monitor(DOOR, POWER)
        #scale = Scale(DATA, CLK)
        #storage = Storage()
        detect = Detect( LED)
    except AttributeError:
        print('Failed to initialize all system components')
        sys.exit()

    ### START DEBUG ###
    detect.timestamp = 'cheese'
    detect.filename = '../data/samples/' + detect.timestamp + '.jpg'
    detect.detectItem()
    detect.parseResponse()

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
#                   
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
#                print('Door must be closed on system start')
#        else:
#            storage.powerWarning()
#    else:
#        pass

# Call main()
if __name__ == '__main__':
    main()
