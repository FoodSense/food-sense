# foodSense.py
# DT08 - Food Sense
# c. 2018 Derrick Patterson and Mavroidis Mavroidis. All rights reserved.

from detect.detect import Detect
from storage.storage import Storage
from scale.scale import Scale
import mcp3008 as ADC
import RPi.GPIO as GPIO
import sys
import time

# Read temp sensor for current fridge temperature
def getTemp(adc):
    print('Reading temperature')

    value = adc()

    if value >= 30.0:
        print('Temperature threshold exceded: ' + str(value))
    else: print('Temperature: ' +str(value))

# Record the current weight on the scale
def getWeight(scale):
    print('Reading from scale')
    
    prevWeight = 0
    weight = (scale.getMeasure()) / 13
    
    # Temporarily account for magnitude mismatch from ckt
    # Will need to be fixed later
    if weight < 0:
        weight = abs(weight)
    print("Weight recorded: {0: 4.6f} g".format(weight))

    # Weight of new item is difference between current and previous weights
    itemWeight = weight - prevWeight
    
    # Need to update what current weight is on scale
    prevWeight = weight
    return itemWeight

# Main method
def main():
    # Pin numbers
    DOOR = 27

    # Get up GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 
    # Begin initializing necessary components
    adc = ADC.MCP3008.fixed([ADC.CH0])                # Create/initialize ADC object for temperature sensor
    scale = Scale()                                   # Create/initialize HX711 object for scale
    scale.setReferenceUnit(20)  # Originally 21
    scale.reset()
    scale.tare()                # Will need to decide how to handle this on system reset.
                                # It may be a good idea to default to the last known weight
                                # on the scale following a tare.
                                # This creates a problem where the system will not know
                                # if a user has added or removed anything in the meantime
    detect = Detect()
    storage = Storage()

    # Main block of program
    try:
        while True:                                             # Loop until an execption is thrown
            while True:# GPIO.input(DOOR) is True:              # Door is closed
                print('Door is closed')
                time.sleep(1)
                
                if True:#GPIO.input(DOOR) is False:             # Door has been opened
                    print('Door was opened')
                    
                    while GPIO.input(DOOR) is False:            # Waiting for door to be closed again
                        print('Waiting for door to close')
                        # Start door timer
                        time.sleep(1)          
                    print('Door was closed')
                    
                    #weight = getWeight(scale)                   # Flagged if item was removed from fridge
                    if detect.weight > 0:
                        detect.getImage()
                        detect.detectLabels()
                        detect.parseRespsone()
                        storage.addItem(item, weight, filename)
                    elif detect.weight < 0:
                        storage.removeItem(weight)
                    else:
                        print('Error: weight is 0')
                    sys.exit()                                   # Exit while loop (for debugging)
            print('Door is open, please close')                  # Warn user that door must be closed on program init
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()

# Call main()
if __name__ == '__main__':
    main()