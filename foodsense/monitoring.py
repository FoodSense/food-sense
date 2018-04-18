import sys
import time

try:
    import RPi.GPIO as GPIO
    import Adafruit_GPIO.SPI as SPI
    import Adafruit_MCP3008
except ImportError:
    print('Failed to import all necessary Monitor packages')
    sys.exit(1)

class Monitoring:
    def __init__(self, firebase, DOOR=5, POWER=6):
        print('Initializing System Monitoring object')

        # Initialize Firebase object as base of Monitoring
        self.fb = firebase
        
        # GPIO Pins
        self.SPI_PORT = 0
        self.SPI_DEVICE = 0
        self.DOOR = DOOR
        self.POWER = POWER

        # Flags for notification frequency
        self.initDoorNotify = False
        self.initPowerNotify = False
        self.initTempNotify = False

        # Max value constants
        self.maxTemp = 10.0
        self.maxDoorTime = 120.0
        self.maxPowerTime = 120.0
        self.maxTempTime = 120.0

        # Notification timers
        self.doorTime = None
        self.powerTime = None
        self.tempTime = None

        # Temperature
        self.temp = None

        # Setup GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.POWER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Initialize MCP3004 ADC object
        self.mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(self.SPI_PORT, self.SPI_DEVICE))

    # Return value from temp sensor adc
    def checkTemp(self):
        self.temp = self.mcp.read_adc(0) / 10

        if self.temp > self.maxTemp:
            if self.initTempNotify is False:
                self.fb.tempWarning()
                self.startTempTimer()
                self.initTempNotify = True
            else:
                self.checkTempTimer()
        else:
            self.initTempNotify = False

        print('Temp: {}C'.format(self.temp))

    # True if door is closed
    def doorClosed(self):  
        return GPIO.input(self.DOOR)

    # True if door is open
    def doorOpen(self):
        return not self.doorClosed()

    # Check that power is on
    def powerOn(self):
        if GPIO.input(self.POWER):
            self.initPowerNotify = False
            return True
        else:
            if self.initPowerNotify is False:
                self.fb.powerWarning()
                self.startPowerTimer()
                self.initPowerNotify = True
            else:
                self.checkPowerTimer()
            return False

    # Wait for power to be restored
    def powerSave(self):
        while not GPIO.input(self.POWER):
            self.checkTemp()

    # Get system time
    def startDoorTimer(self):
        self.doorTime = time.time() 

    # Get system time
    def startPowerTimer(self):
        self.powerTime = time.time()

    # Get system time
    def startTempTimer(self):
        self.tempTime = time.time()

    # Check if door notification timer has been exceeded
    def checkDoorTimer(self):
        if (time.time() - self.doorTime) >= self.maxDoorTime:
            self.fb.doorWarning()

    # Check if power notification timer has been exceeded
    def checkPowerTimer(self):
        if (time.time() - self.powerTime) >= self.maxPowerTime:
            self.fb.powerWarning()

    # Check if temp notification timer has been exceeded
    def checkTempTimer(self):
        if (time.time() - self.tempTime) >= self.maxTempTime:
            self.fb.tempWarning()
