import RPi.GPIO as GPIO
import mcp3008
import time

class System:
    def __init__(self, DOOR, POWER):
        print('Initializing System Monitoring object')
                
        self.__DOOR = DOOR
        self.__POWER = POWER
        self.__maxTemp = 4.4
        self.__time = None

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
    	GPIO.setup(self.__DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    	GPIO.setup(self.__POWER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Initialize MCP3004 ADC object
        self.__adc = mcp3008.MCP3008.fixed([mcp3008.CH0])

    # Return value from temp sensor adc
    def checkTemp(self):
        print('Reading temperature')
        value = self.__adc()
        print(value)
        temp = value    # Need to adjust value here

        if temp > self.__maxTemp:
            return True
        else:
            return False

    # True if door is closed
    def doorClosed(self):
        return GPIO.input(self.__DOOR) is True

    # True if door is open
    def doorOpen(self):
    	return GPIO.input(self.__DOOR) is False

    # Warn that door was left open
    def doorWarning(self):
        print('Door warning')
        time.sleep(1)

    # Return value of power pin
    def powerOn(self):
        print('Checking power status')
        return GPIO.input(self.__POWER)

    # Warn that power has failed
    def powerWarning(self):
        print('Power warning')
        time.sleep(1)

    # Get system time
    def startTimer(self):
        print('Starting door timer')
        self.__time = time.time() 

    # Warn that temp has exceeded limit
    def tempWarning(self):
        print('Temperature warning')
        time.sleep(1)

    # Check if timer has been exceeded
    def timerExceeded(self):
        print('Checking timer')
        if time.time() >= self.__time:
            return True
        else: return False