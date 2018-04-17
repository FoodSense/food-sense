import sys
import time

try:
    import firebase as Firebase
	import RPi.GPIO as GPIO
	import Adafruit_GPIO.SPI as SPI
	import Adafruit_MCP3008
except ImportError:
	print('Failed to import all necessary Monitor packages')
	sys.exit()

class Monitoring(Firebase):
	def __init__(self, DOOR=5, POWER=6):
		print('Initializing System Monitoring object')

        # Initialize Firebase object as base of Monitoring
        Firebase.__init__(self)

		# Member variables
		self.SPI_PORT = 0
		self.SPI_DEVICE = 0
		self.DOOR = DOOR
		self.POWER = POWER
		self.maxTemp = 12.0
		self.temp = None
		self.time = None

		# Setup GPIO
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(self.POWER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

		# Initialize MCP3004 ADC object
		self.mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(self.SPI_PORT, self.SPI_DEVICE))

	# Return value from temp sensor adc
	def checkTemp(self):
		value = self.mcp.read_adc(0)
		self.temp = value / 10

		#print('Raw value: ' + str(value))
		#print('Temp: ' + str(self.temp) + 'C / ' + str(((9*self.temp)/5) + 32) + 'F')

        if self.temp > self.maxTemp:
            Firebase.tempWarning()

	# True if door is closed
	def doorClosed(self):  
		return GPIO.input(self.DOOR)

	# True if door is open
	def doorOpen(self):
		return not GPIO.input(self.DOOR)

	# Check that power is on
	def powerOn(self):
        if GPIO.input(self.POWER):
            return True
        else:
            Firebase.powerWarning()
            return False

    # Wait for power to be restored
    def powerSave(self):
        while not GPIO.input(self.POWER):
            self.checkTemp()

	# Get system time
	def startTimer(self):
		self.time = time.time() 

	# Check if timer has been exceeded
	def checkTimer(self):
		if (time.time() - self.time) >= 120.0:
			Firebase.doorWarning()
