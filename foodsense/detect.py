import base64
import io
import json
import logging
import time
import sys

try:
	from google.oauth2 import service_account
	from googleapiclient import discovery
	from picamera import PiCamera
	import RPi.GPIO as GPIO
except ImportError:
	print('Failed to import required Detect class modules')
	sys.exit()

class Detect:
	def __init__(self, firebase, LED=27):
		print('Initializing Detect object')

		# Reference to Firebase class
		self.fb = firebase

		# Suppress logging errors
		logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
		
		# Cloud Vision authentication
		self.scopes = ['https://www.googleapis.com/auth/cloud-vision']
		self.serviceAccount = '/home/pi/food-sense/service-accounts/foodsense-googlecloud.json'
		#self.serviceAccount = '/home/derrick/food-sense/service-accounts/test-visionapi.json'
		self.credentials = service_account.Credentials.from_service_account_file(
			self.serviceAccount, scopes=self.scopes)
		self.client = discovery.build('vision', 'v1', credentials=self.credentials)

		self.filename = None
		self.items = []
		self.itemNames = [
				'apple', 'apples', 'banana', 'bananas', 'orange', 'oranges', 'tomato', 'tomatoes', 'celery', 
				'cheese', 'ketchup', 'mustard', 'soda', 'pop', 'cola', 'beer', 'milk', 'orange juice'
				]
		self.LED = LED
		self.match = False
		self.response = None
		self.timestamp = None

		# Set up LED pin
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.LED, GPIO.OUT)

	# Use Pi Camera to capture an image; toggle LEDs
	def getImage(self):
		print('Capturing image')
		self.timestamp = time.time()
		self.filename = '../data/images/' + str(self.timestamp) + '.png'

		# Camera init and settings
		with PiCamera() as camera:
			camera.sharpness = 0
			camera.contrast = 0
			camera.brightness = 50
			camera.saturation = 0
			camera.ISO = 0
			camera.exposure_compensation = True
			camera.exposure_mode = 'auto'
			camera.awb_mode = 'auto'
			camera.image_effect = 'none'
			camera.color_effects = None
			camera.rotation = 0
			camera.hflip = False
			camera.vflip = False
			camera.crop = (0.0, 0.0, 1.0, 1.0)
			
			# Turn on LEDs
			GPIO.output(LED, True)

			# Begiin preview, pause for two seconds
			camera.start_preview()
			time.sleep(1.5)

			# Capture image
			camera.capture(self.filename)
		
			# Turn off LEDs
			GPIO.output(LED, False)

	# Detect using custom JSON request
	def detectItem(self):
		print('Detecting item')

		with open(self.filename, 'rb') as image:
			base64img = base64.b64encode(image.read())
			request = self.client.images().annotate(body={
				'requests': [{
					'image': {
						'content': base64img.decode('UTF-8')
					},
					'features': [{
						'type': 'WEB_DETECTION',
						'maxResults': 10
					}]
				}]
			})
		self.response = request.execute()
	
	# Parse Vision API repsonse to find item match
	def parseResponse(self, add=True):
		print('Searching for item match')

		#print(json.dumps(self.response, indent=4, sort_keys=True))

		currList = self.fb.getList()

		bestGuess = self.response['responses'][0]['webDetection']['bestGuessLabels'][0]['label']
		print('Best guess label: {}'.format(bestGuess))

		# Match each "known" item with item(s) in response
		for i in range(len(self.itemNames)):
			if self.itemNames[i] in bestGuess:
				self.items.append(self.itemNames[i]) 
				self.match = True

		# If no items matched, assume best guess label is right
		if self.match is False:
			newItem = bestGuess.replace(' png', '')
			self.items.append(newItem)
		print('Items found: {}'.format(self.items))
