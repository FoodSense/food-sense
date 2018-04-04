# foodSense.py
# DT08 - Food Sense
# c. 2018 Derrick Patterson and Mavroidis Mavroidis. All rights reserved.

##### Include required modules #####
# Basic software modules
import base64
import csv
import io
import json
import sys
import time

# Hardware specific modules
import RPi.GPIO as GPIO
import mcp3008
from picamera import PiCamera
from scale.scale import Scale

# Google Authentication and API modules
#from google.oauth2 import service_account
#from googleapiclient import discovery
from google.cloud import datastore
from google.cloud import vision
from google.cloud.vision import types


##### Method Implementations #####
# Authnticate with Google Vision API
def authenticate():
    print('Authenticating with Google Vision API')
    
    scopes = ['https://www.googleapis.com/auth/cloud-vision']
    serviceAccount = '/home/pi/FoodSense-Service-Account.json'
    
    credentials = service_account.Credentials.from_service_account_file(
        serviceAccount, scopes=scopes)
    return discovery.build('vision', 'v1', credentials=credentials)

# Initialize MCP3004 ADC for temp sensor
def initADC():
    print('Initializing ADC')
    return mcp3008.MCP3008.fixed([mcp3008.CH0])

# Initialize scale, reset and tare
def initScale():
    print('Initializing scale')
    scale = Scale()
    scale.setReferenceUnit(20)  # Originally 21
    scale.reset()
    scale.tare()                # Will need to decide how to handle this on system reset.
                                # It may be a good idea to default to the last known weight
                                # on the scale following a tare.
                                # This creates a problem where the system will not know
                                # if a user has added or removed anything in the meantime

    return scale

def initGCP():
    print('Initializing and authenticating Cloud Platform clients')
    
    return vision.ImageAnnotatorClient(), datastore.Client()

# Read temp sensor for current fridge temperature
def getTemp(adc):
    print('Reading temperature')

    value = adc()

    if value >= 30.0:
        print('Temperature threshold exceded: ' + str(value))
    else: print('Temperature: ' +str(value))

# Record the current weight on the scale
def getWeight(scale):
    print('Reading from scale')
    
    prevWeight = 0
    weight = (scale.getMeasure()) / 13
    
    # Temporarily account for magnitude mismatch from ckt
    # Will need to be fixed later
    if weight < 0:
        weight = abs(weight)
    print("Weight recorded: {0: 4.6f} g".format(weight))

    # Weight of new item is difference between current and previous weights
    itemWeight = weight - prevWeight
    
    # Need to update what current weight is on scale
    prevWeight = weight
    return itemWeight

# Use Pi Camera to capture an image; toggle LEDs
def getImage():
    filename = str(time.time())
    filename += '.png'
    print('File name: '.format(filename))
    
    with picamera.PiCamera() as camera:
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
        print("Image captured")
    
        # Turn off LEDs here
    return filename

# Send JSON request to Vision API
def detect(service, filename):
    print('Sending image to Vision API')
    
    with open(filename, 'rb') as image:
        base64img = base64.b64encode(image.read())
        serviceRequest = service.images().annotate(body={
            'requests': [{
                'image': {
                    'content': base64img.decode('UTF-8')
                },
                'features': [{
                    'type': 'LABEL_DETECTION',
                    'maxResults': 10
                }#,
                #{
                #    'type': 'WEB_DETECTION',
                #    'maxResults': 10
                #}
                ]
            }]
        })
    return serviceRequest.execute()

def detectLabels(client, filename):
    with io.open(filename, 'rb') as imageFile:
        content = imageFile.read()
    image = types.Image(content=content)
    response = client.label_detection(image=image)
    return response.label_annotations

# Parse the response JSON to match item and add to list
def parseRespsone(labels):
    print('Adding item')
    
    itemNames = ['apple', 'banana', 'broccoli', 'celery', 'orange', 'onion', 'potato']
    
    # Find label that matches entry in itemNames
    for i in range(len(itemNames)):
        for j in range(len(labels)):
            if itemNames[i] in labels[j].description:
                item = labels[j].description
            
    #print(json.dumps(labels, indent=4, sort_keys=True))
    #print('')
    
    # Search best guess label for item match
    #for i in range(len(itemNames)): 
    #    if itemNames[i] in response["responses"][0]['webDetection']['bestGuessLabels'][0]['label']:
    #        print('Match found: ' + itemNames[i])

    #responseLen = len(response['responses'][0]['labelAnnotations']) 
    #itemNamesLen = len(itemNames)
    
    # Search label annotations
    #for i in range(responseLen):
    #    for j in range(itemNamesLen):
    #        if itemNames[j] in response["responses"][0]['labelAnnotations'][i]['description']:
    #            print('Label found: ' + itemNames[j])
    #            match = itemNames[j]
    return item

def addItem(item):
    print('Adding item')

# Remove item from list
def removeItem(weight):
    print('Removing item')

def dataStore(client):
    print('Datastore')

    kind = 'Task'
    name = 'sampletask1'
    task_key = client.key(kind, name)

    # Prepares the new entity
    task = datastore.Entity(key=task_key)
    task['description'] = 'Buy milk'

    # Saves the entity
    client.put(task)
    print('Saved {}: {}'.format(task.key.name, task['description']))
    
# Main method
def main():
    # Pin numbers
    DOOR = 27

    # Get up GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 
    # Begin initializing necessary components
    adc = initADC()                                             # Create/initialize ADC object for temperature sensor
    scale = initScale()                                         # Create/initialize HX711 object for scale
    visionClient, datastoreClient = initGCP()
    
    #Attempt to authenticate with Vision API
    #service = authenticate()

    # Main block of program
    try:
        while True:                                             # Loop until an execption is thrown
            while True:# GPIO.input(DOOR) is True:              # Door is closed
                print('Door is closed')
                time.sleep(1)
                
                if True:#GPIO.input(DOOR) is False:             # Door has been opened
                    print('Door was opened')
                    
                    while GPIO.input(DOOR) is False:            # Waiting for door to be closed again
                        print('Waiting for door to close')
                        time.sleep(1)          
                    print('Door was closed')
                    
                    #weight = getWeight(scale)                   # Flagged if item was removed from fridge
                    weight = 50
                    if weight > 0:
                        #filename = getImage()
                        #response = detect(service, 'samples/apple.jpg')
                        labels = detectLabels(visionClient, 'samples/apple.jpg')
                        item = parseRespsone(labels)
                        print(item)
                        #dataStore(datastoreClient)
                        #addItem(item)
                    elif weight < 0:
                        removeItem(weight)
                    else:
                        print('Error: weight is 0')
                    sys.exit()                                   # Exit while loop (for debugging)
            print('Door is open, please close')                  # Warn user that door must be closed on program init
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()

##### Program entrypoint #####
# Call main()
if __name__ == '__main__':
    main()
