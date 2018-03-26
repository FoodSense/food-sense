# foodSense.py
# DT08 - Food Sense
# c. 2018 Derrick Patterson and Mavroidis Mavroidis. All rights reserved.

import base64
import io
import json
import sys
import time
import RPi.GPIO as GPIO
import mcp3008
import picamera
from picamera import PiCamera
from scale.scale import Scale
from google.cloud import datastore
from google.cloud import vision
from google.cloud.vision import types


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

# Authenticate with Vision API and Cloud Datastore
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
    filename = 'data/images/' + str(time.time()) + '.png'
    print(filename)
    
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

def detectLabels(client, filename):
    print('Detecting labels')
    
    with io.open(filename, 'rb') as imageFile:
        content = imageFile.read()
    image = types.Image(content=content)
    response = client.label_detection(image=image)
    return response.label_annotations

# Parse the response JSON to match item and add to list
def parseRespsone(labels):
    print('Searching for label match')
    
    #for label in labels:
    #    print(label.description)
    
    itemNames = ['apple', 'banana', 'broccoli', 'celery', 'orange', 'onion', 'potato', 'tomato', 'soda', 'beer', 'milk', 'cheese']
    
    # Find label that matches entry in itemNames
    for i in range(len(itemNames)):
        for j in range(len(labels)):
            if itemNames[i] == labels[j].description:
                item = labels[j].description
    return item

# Add item to Datastore
def addItem(client, item, weight, filename):
    print('Adding item to list')
    
    kind = 'Contents'
    name = item
    task_key = client.key(kind, name)

    # Prepares the new entity
    task = datastore.Entity(key=task_key)
    task['weight'] = weight
    task['date/time'] = filename

    # Saves the entity
    client.put(task)
    print('Saved {}: {}, {}'.format(task.key.name, task['weight'], task['date/time']))

# Remove item from Datastore
def removeItem(client, weight):
    print('Removing item')

# Search Datastore for item
def searchList(client, item, weight):
    print('Searching datastore')

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
                        # Start door timer
                        time.sleep(1)          
                    print('Door was closed')
                    
                    #weight = getWeight(scale)                   # Flagged if item was removed from fridge
                    weight = 50
                    if weight > 0:
                        #filename = getImage()
                        filename = 'data/samples/potato.jpg'
                        labels = detectLabels(visionClient, filename)
                        item = parseRespsone(labels)
                        addItem(datastoreClient, item, weight, filename)
                    elif weight < 0:
                        removeItem(datastoreClient, weight)
                    else:
                        print('Error: weight is 0')
                    sys.exit()                                   # Exit while loop (for debugging)
            print('Door is open, please close')                  # Warn user that door must be closed on program init
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()

# Call main()
if __name__ == '__main__':
    main()