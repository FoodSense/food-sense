from google.oauth2 import service_account
from googleapiclient import discovery
from picamera import PiCamera
import RPi.GPIO as GPIO
import base64
import io
import json
import logging

class Detect:
    def __init__(self, LED):
        print('Initializing Detect object')
        
        # Suppress logging errors
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
        
        # Cloud Vision authentication
        self.__scopes = ['https://www.googleapis.com/auth/cloud-vision']
        self.__serviceAccount = '/home/pi/FoodSense-GoogleCloud.json'
        
        self.__credentials = service_account.Credentials.from_service_account_file(
            self.__serviceAccount, scopes=self.__scopes)
        self.__client = discovery.build('vision', 'v1', credentials=self.__credentials)
        
        # Private class members
        self.__itemNames = ['apple', 'banana', 'broccoli', 'celery',
                            'orange', 'onion', 'potato', 'tomato',
                            'soda', 'beer', 'milk', 'cheese']
        self.__LED = LED
        self.filename = None
        self.__match = False
        self.__response = None
        
        # Public class members
        self.timestamp = None
        self.item = None

        # Set up LED pin
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(self.__LED, GPIO.OUT)

    # Use Pi Camera to capture an image; toggle LEDs
    def getImage(self):
        print('Capturing image')
        self.timestamp = time.time()
        self.__filename = 'data/images/' + str(timestamp) + '.png'

        # Camera init and settings
        with PiCamera.PiCamera() as camera:
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
            
            # Turn on LEDs here

            # Begiin preview, pause for two seconds
            camera.start_preview()
            time.sleep(1.5)

            # Capture image
            camera.capture(filename)
        
            # Turn off LEDs here

    # Detect using custom JSON request
    def detectItem(self):
        print('Detecting item')

        with open(self.filename, 'rb') as image:
            base64img = base64.b64encode(image.read())
            request = self.__client.images().annotate(body={
                'requests': [{
                    'image': {
                        'content': base64img.decode('UTF-8')
                    },
                    'features': [{
                        'type': 'LABEL_DETECTION',
                        'maxResults': 5
                    },
                    {
                        'type': 'WEB_DETECTION',
                        'maxResults': 5
                    }]
                }]
            })
        self.__response = request.execute()
    
    # Parse Vision API repsonse to find item match
    def parseResponse(self):
        print('Searching for item match')

        #print(json.dumps(self.__response, indent=4, sort_keys=True))
        #print('')

        #for i in range(5):
        #    print(self.__response['responses'][0]['labelAnnotations'][i]['description'])
        #    print('')
        #    print(self.__response['responses'][0]['webDetection']['webEntities'][i]['description'])
        #    print('')

        # Find match in label annotations
        for i in range(len(self.__response['responses'][0]['labelAnnotations'])):
            for j in range(len(self.__itemNames)):
                if self.__itemNames[j] == self.__response["responses"][0]['labelAnnotations'][i]['description']:
                    self.__match = True
                    self.item = self.__response["responses"][0]['labelAnnotations'][i]['description']

        # If no match found, try web detection
        if self.__match is False:
            for i in range(len(self.__response['responses'][0]['webDetection']['webEntities'])):
                for j in range(len(self.__itemNames)):
                    if self.__itemNames[j] == self.__response["responses"][0]['webDetection']['webEntities'][i]['description']:
                        self.__match = True
                        self.item = self.__response["responses"][0]['webDetection']['webentities'][i]['description']


        # If no match still found, try logo detection
        #if self.__match is False:
        #    for i in range(len(self.__response['responses'][0]['logoAnnotations'])):
        #        for j in range(len(self.__itemNames)):
        #            if self.__itemNames[j] == self.__response["responses"][0]['logoAnnotations'][i]['description']:
        #                self.__match = True
        #                self.item = self.__response["responses"][0]['logoAnnotations'][i]['description']

        # Last resort: ask user for input
        if self.__match is False:
            self.item = 'Null'	
