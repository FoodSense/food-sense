#!/usr/bin/python3
import base64
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
    sys.exit(1)


class Detect:
    def __init__(self, firebase, queue):        
    	print('Initializing Detect')

        # Initialize Firebase object as base of Detect
        self.fb = firebase

        # Queue
        self.q = queue

        # Suppress logging errors
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

        # Cloud Vision authentication
        self.scopes = ['https://www.googleapis.com/auth/cloud-vision']
        self.serviceAccount = '/home/pi/food-sense/service-accounts/foodsense-googlecloud.json'
        self.credentials = service_account.Credentials.from_service_account_file(
            self.serviceAccount, scopes=self.scopes)
        self.client = discovery.build('vision', 'v1', credentials=self.credentials)

        # Class member variables
        self.filename = None
        self.items = []
        self.knownItems = [
                'apple', 'apples', 
                'banana', 'bananas', 
                'beer',
                'carrot', 'carrots',
                'cheese',
                'cola', 'pop', 'soda',
                'ketchup',
                'milk',
                'mustard',
                'orange', 'oranges', 
                'tomato', 'tomatoes',      
                'water',
                ]

        self.knownItemsLen = len(self.knownItems)
        self.LED = LED
        self.match = False
        self.response = None
        self.timestamp = None

    # Use Pi Camera to capture an image; toggle LEDs
    def getImage(self):
        print('Capturing image')
        self.q.put('Capturing image')
        
        self.timestamp = time.time()
        self.filename = '/home/pi/food-sense/images/' + str(self.timestamp) + '.jpg'

        # Camera init and settings
        with PiCamera() as camera:
            camera.sharpness = 0
            camera.contrast = 25
            camera.brightness = 50
            camera.saturation = 0
            camera.ISO = 0
            camera.exposure_compensation = True
            camera.exposure_mode = 'backlight'
            camera.awb_mode = 'fluorescent'
            camera.image_effect = 'colorbalance'
            camera.color_effects = None
            camera.drc_strength = 'off'
            camera.rotation = 0
            camera.hflip = False
            camera.vflip = False
            camera.crop = (0.0, 0.0, 1.0, 1.0)

            # Capture image
            camera.capture(self.filename)

    # Detect using custom JSON request
    def detectItem(self):
        print('Detecting item')
        self.q.put('Detecting item')

        with open(self.filename, 'rb') as image:
            base64img = base64.b64encode(image.read())
            request = self.client.images().annotate(body={
                'requests': [{
                    'image': {
                        'content': base64img.decode('UTF-8')
                    },
                    'features': [{
                        'type': 'WEB_DETECTION',
                        'maxResults': 10,
                        },
                        {
                        'type': 'LABEL_DETECTION',
                        'maxResults' : 10,
                    }]
                }]
            })
        self.response = request.execute()
    
    # Parse Vision API repsonse to find items
    # This is most effective when only adding or removing
    # one item at a time, especially "known" items.
    def parseResponse(self, weight):
        print('Searching for item match')
        self.q.put('Searching for item match')

        match = False
        matched = []
        unmatched = []
        
        # Get current list of items from Firebase
        currList = self.fb.getList()
        listLen = len(currList)
        print('Current list: {}'.format(currList))

        # Get best guess label from response
        bestGuess = (self.response['responses'][0]['webDetection']['bestGuessLabels'][0]['label']).lower()

        # Get web entities from response
        webLength = len(self.response['responses'][0]['webDetection']['webEntities'])
        webEntities = [0]*webLength
        for i in range(webLength):
            if 'description' not in self.response['responses'][0]['webDetection']['webEntities'][i]:
                webEntities[i] = ''
            else:
                webEntities[i] = (self.response['responses'][0]['webDetection']['webEntities'][i]['description']).lower()
            
        # Get label annotations from response
        labelLength = len(self.response['responses'][0]['labelAnnotations'])
        labelAnnotations = [0]*labelLength
        for i in range(labelLength):
            if 'description' not in self.response['responses'][0]['labelAnnotations'][i]:
                labelAnnotations[i] = ''
            else:
                labelAnnotations[i] = (self.response['responses'][0]['labelAnnotations'][i]['description']).lower()

        print('Best guess: {}'.format(bestGuess))
        print('Web entities: {}'.format(webEntities))
        print('Label annotations: {}'.format(labelAnnotations))

        # Match each predetermined item with item(s) in response
        for i in range(self.knownItemsLen):
            if self.knownItems[i] in bestGuess:
                matched.append(self.knownItems[i]) 

        # If best guess doesn't match, try web entities
        matched.extend([item for item in self.knownItems if item in webEntities])

        # If web entities doesn't match, try label annotations
        matched.extend([item for item in self.knownItems if item in labelAnnotations])

        # Remove duplicate entries
        matched = list(set(matched))
        
        # Determine what in fridge were not found from the image
        for item in currList:
            if item in matched:
                pass
            else:
                unmatched.append(item)

        print('Item(s) found: {}'.format(matched))
        self.q.put('Adding to list: {}'.format(matched))
        
        print('Items in list that were not found: {}'.format(unmatched))
        self.q.put('Removing from list: {}'.format(unmatched))
        
        # Remove all items that were not found in response
        for item in unmatched:
            self.fb.removeItem(item)
            self.fb.addShopping(item)

        # Add all items that were found in response
        #for i in range(matchedLen):
        matchedLen = len(matched)
        for item in matched:
            if matchedLen > 1:
                self.timestamp += 1
            self.fb.addItem(item, str(weight/matchedLen), str(self.timestamp))
            self.fb.removeShopping(item)

        # Upload latest image to Firebase Storage
        if matched:
            self.fb.uploadImage(self.filename)
