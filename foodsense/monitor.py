#import RPi.GPIO as GPIO
#import mcp3008
import sys
import time

class Monitor:
    def __init__(self, storage, DOOR, POWER):
        print('Initializing System Monitoring object')
                
        self.DOOR = DOOR
        self.POWER = POWER
        self.maxTemp = 4.4
        self.time = None

        # Setup GPIO
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(self.DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        #GPIO.setup(self.POWER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Initialize MCP3004 ADC object
        #self.adc = mcp3008.MCP3008.fixed([mcp3008.CH0])

    ### SENSOR READINGS ###
    
    # Return value from temp sensor adc
    def checkTemp(self):
        print('Reading temperature')
        
        #value = self.adc()
        #print(value)
        #temp = value    # Need to adjust value here

        #if temp > self.maxTemp:
        #    return True
        #else:
        #    return False

    # True if door is closed
    def doorClosed(self):  
        #return GPIO.input(self.DOOR) is True

    # True if door is open
    def doorOpen(self):
    	#return GPIO.input(self.DOOR) is False

    # Return value of power pin
    def powerOn(self):
        print('Checking power status')
        
        #return GPIO.input(self.POWER)

    ### TIMERS ###
    
    # Get system time
    def startTimer(self):
        print('Starting door timer')
        
        self.time = time.time() 

    # Check if timer has been exceeded
    def timerExceeded(self):
        print('Checking timer')
        
        if time.time() >= self.time:
            return True
        else: return False
