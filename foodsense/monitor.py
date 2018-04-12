import sys
import time

try:
    import RPi.GPIO as GPIO
    import Adafruit_GPIO.SPI as SPI
    import Adafruit_MCP3008
except ImportError:
    print('Failed to import all necessary Monitor packages')
    sys.exit()

class Monitor:
    def __init__(self, DOOR, POWER):
        print('Initializing System Monitoring object')
               
        # Member variables
        self.SPI_PORT = 0
        self.SPI_DEVICE = 0
        self.DOOR = DOOR
        self.POWER = POWER
        self.maxTemp = 4.4
        self.temp = None
        self.time = None

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.POWER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Initialize MCP3004 ADC object
        self.mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(self.SPI_PORT, self.SPI_DEVICE))

    # Return value from temp sensor adc
    def checkTemp(self):
        value = self.mcp.read_adc(0)
        self.temp = value / 10

        print('Raw value: ' + str(value))
        print('Temp: ' + str(self.temp) + 'C / ' + str(((9*self.temp)/5) + 32) + 'F')

        if (self.temp >= self.maxTemp):
            return True
        else:
            return False

    # True if door is closed
    def doorClosed(self):  
        return GPIO.input(self.DOOR) is True

    # True if door is open
    def doorOpen(self):
    	return GPIO.input(self.DOOR) is False

    # Return value of power pin
    def powerOn(self):
        return GPIO.input(self.POWER)

    ### TIMERS ###

    # Get system time
    def startTimer(self):
        self.time = time.time() 

    # Check if timer has been exceeded
    def timerExceeded(self):
        if (time.time() - self.time) >= 10.0:
            return True
        else:
            return False
