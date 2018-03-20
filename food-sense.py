# foodSense.py
# DT08 - Food Sense
# c. 2018 Derrick Patterson and Mavroidis Mavroidis. All rights reserved.


##### Include required modules #####
# Basic software modules
import base64
import csv
import json
import sys
import time

# Hardware specific modules
import RPi.GPIO as GPIO
import mcp3008
from picamera import PiCamera
from scale import Scale

# Google Authentication and API modules
from google.oauth2 import service_account
from googleapiclient import discovery


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


# Read temp sensor for current fridge temperature
def getTemp(adc):
    print('Reading temperature')

    value = adc()

    if value >= 30.0:
        print('Temperature threshold exceded: ' + str(value))
    else: print('Temperature: ' +str(value))


# Record the current weight on the scale
def getWeight(scale):
    itemRemoved = False
    
    # Will have to get prevWeight from db, using 0 for now
    prevWeight = 0
    
    currWeight = (scale.getMeasure()) / 13
    
    # Temporarily account for magnitude mismatch from ckt
    # Will need to be fixed later
    if currWeight < 0:
        currWeight = abs(currWeight)
    print("Weight recorded: {0: 4.6f} g".format(currWeight))
    print('')

    # Weight of new item is difference between current and previous weights
    itemWeight = currWeight - prevWeight

    # If an item is removed, weight difference will be negative
    if itemWeight < 0:
        itemWeight = abs(itemWeight)
        itemRemoved = True
        
    scaleLoad = currWeight
    weightList.append(itemWeight)
    return itemRemoved


# Use Pi Camera to capture an image; toggle LEDs
def getImage():
    filename = str(time.time())
    filename += '.png'
    print('File name: '.format(filename))
    
    print("Initializing camera")
    camera = PiCamera()

    # Turn on LEDs here

    print("Starting camera preview")
    camera.start_preview()
    time.sleep(3)

    camera.capture(filename)
    camera.close()
    print("Image captured")
    
    # Turn off LEDs here
    
    return filename


# Send JSON request to Vision API
def detect(service, filename):
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
                },
                {
                    'type': 'WEB_DETECTION',
                    'maxResults': 10
                }]
            }]
        })

    return serviceRequest.execute()


# Remove item from list
def removeItem():
    print('Removing item')


# Parse the response JSON to match item and add to list
def parseRespsone(response):
    print('Adding item')
    
    match = False
    itemNames = ['apple', 'banana', 'broccoli', 'celery', 'orange', 'onion', 'potato']
    itemDescriptors = ['fruit', 'vegitable', 'produce', 'organic', 'apple', 'banana', 'broccoli', 'celery', 'orange', 'potato']
    
    #print(json.dumps(response, indent=4, sort_keys=True))
    
    # Search best guess label for item match
    #for i in range(len(itemNames)): 
    #    if itemNames[i] in response["responses"][0]['webDetection']['bestGuessLabels'][0]['label']:
    #        print('Match found: ' + itemNames[i])

    for i in range(10):
        print(response['responses'][0]['webDetection']['webEntities'][i]['description'])

    # Search web detection lables
    #if match is False:
    #    for i in range(10):
    #        for j in range(len(itemNames)):
    #            if itemNames[j] in response["responses"][0]['webDetection']['webEntities'][i]['description']:
    #                print('Web Entity found: ' + itemNames[j])
    #                match = True
   
   # Search label annotations
    #if match is False:
    #    for i in range(10):
    #        for j in range(len(itemNames)):
    #            if itemNames[j] in response["responses"][0]['labelAnnotations'][i]['description']:
    #                print('Label found: ' + itemNames[j])
    #                match = True

# Main method
def main():
    # Pin numbers
    DOOR = 27

    # Get up GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 
    # Open file stream for loading/saving item information
    #itemListFile = open('data/itemList.csv')
  
    # Begin initializing necessary components
    #adc = initADC()                                             # Create/initialize ADC object for temperature sensor
    #scale = initScale()                                         # Create/initialize HX711 object for scale

    # Attempt to authenticate with Vision API
    service = authenticate()

    # Main block of program
    try:
        while True:         # Loop until an execption is thrown
            while True:# GPIO.input(DOOR) is True:              # Door is closed
                print("Door is closed")
                time.sleep(1)
                
                if True:#GPIO.input(DOOR) is False:             # Door has been opened
                    print("Door was opened")
                    
                    while GPIO.input(DOOR) is False:            # Waiting for door to be closed again
                        print("Waiting for door to close")
                        time.sleep(1)          
                    print("Door was closed")
                    
                    #weight = getWeight(scale)                   # Flagged if item was removed from fridge
                    weight = 50
                    if weight > 0:
                        #filename = getImage()
                        response = detect(service, 'samples/apple.jpg')
                        parseRespsone(response)
                    elif weight < 0:
                        removeItem()
                    else:
                        print('Error: weight is 0')
                    sys.exit()
                    
            print('Door is open, please close')                 # Warn user that door must be closed on program init

    except KeyboardInterrupt:
        # Write list values to files
        GPIO.cleanup()
        sys.exit()


##### Program entrypoint #####
# Call main()
if __name__ == '__main__':
    main()
