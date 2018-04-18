import base64
import io
import json
import logging
import time
import sys

try:
    from firebase import Firebase
    from google.oauth2 import service_account
    from googleapiclient import discovery
    #from picamera import PiCamera
    #import RPi.GPIO as GPIO
except ImportError:
	print('Failed to import required Detect class modules')
	sys.exit()

class Detect(Firebase):
    def __init__(self, LED=27):
        print('Initializing Detect object')

        # Initialize Firebase object as base of Detect
        Firebase.__init__(self)

        # Suppress logging errors
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

		# Cloud Vision authentication
        self.scopes = ['https://www.googleapis.com/auth/cloud-vision']
        #self.serviceAccount = '/home/pi/food-sense/service-accounts/foodsense-googlecloud.json'
        self.serviceAccount = '/home/derrick/food-sense/service-accounts/test-googlecloud.json'
        self.credentials = service_account.Credentials.from_service_account_file(
            self.serviceAccount, scopes=self.scopes)
        self.client = discovery.build('vision', 'v1', credentials=self.credentials)

        self.filename = None
        self.items = []
        self.itemNames = [
				'apple', 'apples', 'banana', 'bananas', 'orange', 'oranges', 
                'tomato', 'tomatoes', 'celery', 'cheese', 'ketchup', 'mustard', 
                'soda', 'pop', 'cola', 'beer', 'founders all day ipa', 'water', 
                'bottled water'
				]

        self.LED = LED
        self.match = False
        self.response = None
        self.timestamp = None

		# Set up LED pin
		#GPIO.setwarnings(False)
		#GPIO.setmode(GPIO.BCM)
		#GPIO.setup(self.LED, GPIO.OUT)

	# Use Pi Camera to capture an image; toggle LEDs
    def getImage(self):
        print('Capturing image')
	    self.timestamp = time.time()
        self.filename = '../images/' + str(self.timestamp) + '.png'

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
            GPIO.output(self.LED, True)

			# Begiin preview, pause for two seconds
            camera.start_preview()
            time.sleep(1.5)

			# Capture image
            camera.capture(self.filename)
		
			# Turn off LEDs
            GPIO.output(self.LED, False)

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
	
	# Parse Vision API repsonse to find items
    # This is most effective when only adding or removing
    # one item at a time, especially "known" items.
	def parseResponse(self, weight=0):
		print('Searching for item match')
		#print(json.dumps(self.response, indent=4, sort_keys=True))

        self.items = []     # Clear item list

        # Get current list of items from Firebase
		currList = Firebase.getList()
		print('Current list: {}'.format(currList))

        # Get best guess label from response
		bestGuess = self.response['responses'][0]['webDetection']['bestGuessLabels'][0]['label']
		print('Best guess: {}'.format(bestGuess))

		# Match each "known" item(s) with item(s) in response
		for i in range(len(self.itemNames)):
			if self.itemNames[i] in bestGuess:
				self.items.append(self.itemNames[i]) 
				self.match = True

		# If no specific item(s) matched, assume best guess label is right
        # This could cause unexpected items, like walls, to be added to list
		#if self.match is False:
		#	newItem = bestGuess.replace(' png', '')
		#	self.items.append(newItem)
		print('Item(s) found: {}'.format(self.items))
		
        # Determine what items in list are not in response
		itemSet = set(self.items)
		listSet = set(currList)
		unmatched = itemSet.symmetric_difference(listSet)
		print('Items in list that were not found in image: {}'.format(unmatched))
		
        # Remove all items that were not found in response
        for i in unmatched:
            Firebase.removeItem(str(i))
            Firebase.addShopping(str(i))

        # Add all items that were found in response
        numItems = len(self.items)
        for i in range(numItems):
		    Firebase.addItem(str(self.items[i]), str(weight/numItems), str(self.timestamp+=i))
            Firebase.removeShopping(str(self.items[i]))

        # Upload latest image to Firebase Storage
        Firebase.uploadImage(self.filename)
