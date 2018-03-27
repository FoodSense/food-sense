from google.cloud import vision
from google.cloud.vision import types
from picamera import PiCamera
import io
#import json

class Detect:
    def __init__(self):
        print('Initializing Detect object')
        
        self.__client = vision.ImageAnnotatorClient()
        self.__itemNames = ['apple', 'banana', 'broccoli', 'celery',
                            'orange', 'onion', 'potato', 'tomato',
                            'soda', 'beer', 'milk', 'cheese']
        self.__labels = None
        self.filename = None
        self.item = None

    # Use Pi Camera to capture an image; toggle LEDs
    def getImage():
        print('Capturing image')
        
        filename = 'data/images/' + str(time.time()) + '.png'
        
        with PiCamera.PiCamera() as camera:
            # Camera settings
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
    
    # Detect object in image
    def detectLabels(self):
        print('Detecting labels')
        
        with io.open(self.filename, 'rb') as imageFile:
            content = imageFile.read()
        image = types.Image(content=content)
        response = self.client.label_detection(image=image)
        self.__labels = response.label_annotations

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