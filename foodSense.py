# foodSense.py
# DT08 - Food Sense
# c. 2018 Derrick Patterson and Mavroidis Mavroidis. All rights reserved.

from detect.detect import Detect
from storage.storage import Storage
from scale.scale import Scale
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

# Main method
def main():
    print('Starting Food Sense')
    
    # GPIO pins
    DATA = 22      # Data pin for HX711 ADC
    DOOR = 27      # Door pin
    LED = None     # LED pin
    POWER = None   # Power monitoring pin
    SCK = 17       # CLK pin for HX711 ADC

    # Set up GPIO pins
    #try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    #GPIO.setup(POWER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    #GPIO.setup(LED, GPIO.OUT)
    #except
    #    print('Failed to setup GPIO pins')
    #    sys.exit()
        
    # Begin initializing necessary components
    try: 
        detect = Detect()
        monitor = Monitor()
        scale = Scale(DATA, SCK)
        storage = Storage()
    except AttributeError:
        print('Failed to initialize all system components')
        sys.exit()
        
    # Main program loop
    try:
        while True:#GPIO.input(POWER) is True:
            while True:# GPIO.input(DOOR) is True:
                print('Door is closed')
                time.sleep(1)
                
                if True:#GPIO.input(DOOR) is False:  
                    print('Door was opened')
                    
                    while GPIO.input(DOOR) is False:  
                        print('Waiting for door to close')
                        # Start door timer
                        time.sleep(1)          
                    print('Door was closed')
                    
                    #scale.getWeight()
                    scale.weight = 50
                    if scale.weight > 0:
                        detect.getImage()
                        detect.detectLabels()
                        detect.parseRespsone()
                        storage.addItem(detect.item, scale.weight, detect.filename)
                    elif scale.weight < 0:
                        storage.removeItem(scale.weight)
                    else:
                        print('Error: weight is 0')
                    sys.exit()     
            print('Door is open, please close') 
        print('Power failure')
        sys.exit()
        
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()

# Call main()
if __name__ == '__main__':
    main()