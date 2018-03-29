#from google.cloud import vision
#from google.cloud.vision import types
from google.oauth2 import service_account
from googleapiclient import discovery
from picamera import PiCamera
import RPi.GPIO as GPIO
import base64
import io
#import json

class Detect:
    def __init__(self, LED):
        print('Initializing Detect object')
        
        #self.__client = vision.ImageAnnotatorClient()
        self.__scopes = ['https://www.googleapis.com/auth/cloud-vision']
        self.__serviceAccount = '/home/pi/FoodSense-Service-Account.json'
        self.__credentials = service_account.Credentials.from_service_account_file(
            serviceAccount, scopes=scopes)
        self.__client = discovery.build('vision', 'v1', credentials=credentials)
        self.__response = None
        self.__itemNames = ['apple', 'banana', 'broccoli', 'celery',
                            'orange', 'onion', 'potato', 'tomato',
                            'soda', 'beer', 'milk', 'cheese']
       #self.__labels = None
        self.__LED = LED
        self.filename = None
        self.item = None
        self.__match = False

        # Set up LED pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__LED, GPIO.OUT)

    # Use Pi Camera to capture an image; toggle LEDs
    def getImage(self):
        print('Capturing image')
        self.filename = 'data/images/' + str(time.time()) + '.png'

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
                    'type': 'LOGO_DETECTION',
                    'maxResults': 3
                }]
            }]
        })
    self.__response = request.execute()
    
    # Detect object in image
    #def detectLabels(self):
    #    print('Detecting labels')
    #    
    #    with io.open(self.filename, 'rb') as imageFile:
    #        content = imageFile.read()
    #    image = types.Image(content=content)
    #    response = self.client.label_detection(image=image)
    #    self.__labels = response.label_annotations

    # Parse the response JSON to match item and add to list
    def parseRespsone(self):
        print('Searching for label match')
        
        #for label in labels:
        #    print(label.description)
                     
        # Find label that matches entry in itemNames
        for i in range(len(self.__itemNames)):
            for j in range(len(self.__labels)):
                if self.__itemNames[i] == self.__labels[j].description:
                    self.item = self.__labels[j].description


    def parseResponse(self):
        print('Searching for item match')

        for i in range(len(self.__response['responses'][0]['labelAnnotations'])):
            for j in range(len(self.__itemNames)):
                if self.__itemNames[j] == self.__response["responses"][0]['labelAnnotations'][i]['description']:
                    self.__match = True
                    self.item = self.__response["responses"][0]['labelAnnotations'][i]['description']
            if match is False: