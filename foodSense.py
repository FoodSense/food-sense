# Include required modules
import base64
import csv
import io
import json
import os
import time
import sys

# Hardware specific modules
import RPi.GPIO as GPIO
import spidev as SPI
#import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from picamera import PiCamera
from scale import Scale

# Google Authentication and API modules
from google.oauth2 import service_account
from googleapiclient import discovery


# Global variables for adding/removing items
global scaleLoad       # Current load on scale
global itemList[]      # List of items
global weightList[]    # List of weights

# Authnticate with Google Vision API
def authenticate():
    print('Authenticating with Google Vision API')
    
    scopes = ['https://www.googleapis.com/auth/cloud-vision']
    serviceAccount = '/home/pi/FoodSense-Service-Account.json'
    
    credentials = service_account.Credentials.from_service_account_file(
        serviceAccount, scopes=scopes)
    return discovery.build('vision', 'v1', credentials=credentials)


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
def getTemp():
    print('Reading temperature')
rom time import sleep


def readTemp(mcp):
    adcValue = mcp.read_adc(0)
    tempC = adcValue / 10
    tempF = (tempC * 1.8) + 32
    print('Current temperature: ' + str(tempC) + ' C / ' + str(tempF) + ' F')

def main():
    SPI_PORT   = 0
    SPI_DEVICE = 0
    mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

    try:
        while True:
            readTemp(mcp)
            sleep(3)
 

# Use Pi Camera to capture an image; toggle LEDs
def getImage():
    filename = str(time.time())
    filename += '.png'
    #print(filename)
    
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
                    'type': 'WEB_DETECTION',
                    'maxResults': 3
                },
                {
                    'type': 'LABEL_DETECTION',
                    'maxResults': 3
                }]
            }]
        })

    return serviceRequest.execute()


# Remove item from list based on weight
def removeItem():
    print('Removing item')


# Parse the response JSON to match item
def addItem(response):
    print('Adding item')

    match = False
    itemNames = ['granny smith', 'bread', 'apple', 'banana', 'milk', 'fruit', 'vegitable']
    itemDescriptors = ['fruit', 'vegitable', 'produce', 'organic', 'apple', 'granny smith']
    
    # Search best guess label for item match
    for i in range(len(itemNames)): 
        if itemNames[i] in response["responses"][0]['webDetection']['bestGuessLabels'][0]['label']:
            print('Match found: ' + itemNames[i])
            itemList.append(itemnames[i])
            match = True

    # If best guess label does not match, search label annotations
    if match is False:
        for i in range(3):
            for j in range(len(itemDescriptors)):
                if itemDescriptors[j] in response["responses"][0]['labelAnnotations'][i]['description']:
                    print('Label found: ' + itemDescriptors[j])

    # If label anotations does not match, ask user for input


# Entrypoint
def main():
    # GPIO Pins used
    DOOR = 27

    # Set up GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 
    # Open saved list information and read into global variables
    itemListFile = open('itemList.csv', 'r+')
    itemList.append(itemListFile.read())

    weightListFile = open('weightListFile.csv', 'r+')
    weightlist.append(weightListFile.read())

    # Authenticate and init scale
    service = authenticate()
    scale = initScale()

    try:
        # Loop until an execption is thrown
        while True:

            # Door is closed
            while GPIO.input(DOOR) is True:
                print("Door is closed")
                time.sleep(1)
                
                # Door has been opened
                if GPIO.input(DOOR) is False:
                    print("Door was opened")
                    
                    # Waiting for door to be closed again
                    while GPIO.input(DOOR) is False:
                        print("Waiting for door to close")
                        time.sleep(1)          
                    print("Door was closed")
                    
                    itemRemoved = getWeight(scale)
                    if itemRemoved is True:
                        removeItem()
                    else: 
                        filename = getImage()
                        response = detect(service, filename)
                        addItem(response)

            # Door was open when program started;
            # Warn that is must be closed first
            print('Door is open, please close')

    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()


# Call main
if __name__ == '__main__':
    main()
