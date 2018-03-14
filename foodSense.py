# foodSense.py - Testing the Google Cloud Platform (GCP) Vision API with fridge door sensor acting as a trigger
# Built utilizing GCP Vision API and python.org documentation

# Include required packages
import base64
import json
import os
import time
import sys
import RPi.GPIO as GPIO

from google.cloud import vision
import google.auth

#from googleapiclient import discovery
#from oauth2client.client import GoogleCredentials

from picamera import PiCamera
from scale import Scale


def authenticate():
    print('Authenticating with Google Vision API')
  
    #GOOGLE_APPLICATION_CREDENTIALS = "~/gcp-service-account.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "fs-service-account.json"
    credentials, project = google.auth.default()
    
    if credentials.requires_scopes:
        credentials = credentials.with_scopes(['https://vision.googleapis.com/v1/images:annotate'])
    client = vision.Client(credentials=credentials)
    buckets = client.list_buckets()
    
    for bkt in buckets:
        print(bkt)

    #credentials = GoogleCredentials.get_application_default()
    #return discovery.build('vision', 'v1', credentials=credentials)


def initScale():
    print('Initializing scale')
    scale = Scale()
    scale.setReferenceUnit(21)
    scale.reset()
    scale.tare()

    return scale


def getImage():
    filename = str(time.time())
    filename += '.png'
    #print(filename)
    
    print("Initializing camera")
    camera = PiCamera()

    print("Starting camera preview")
    camera.start_preview()
    time.sleep(3)

    camera.capture(filename)
    camera.close()
    print("Image captured")
    
    return filename


def getWeight(scale):
    val = (scale.getMeasure()) / 13
        
    if val < 0:
        val = abs(val)
    print("Weight recorded: {0: 4.6f} g".format(val))
    print('')


def detect(service, filename):
    with open(filename, 'rb') as image:
        base64img = base64.b64encode(image.read())
        service_request = service.images().annotate(body={
            'requests': [{
                'image': {
                    'content': base64img.decode('UTF-8')
                },
                'features': [{
                    'type': 'LABEL_DETECTION',
                    'maxResults': 3
                },
                {
                    'type': 'WEB_DETECTION',
                    'maxResults': 3
                }]
            }]
        })

    return service_request.execute()


def parse(response):
    noLabel = False
    labelResults = 3
    itemLabels = ['granny smith', 'Granny Smith', 'bread', 'apple', 'banana', 'milk', 'fruit', 'vegitable']

    #print('Response JSON:')
    #print(json.dumps(response, indent=4, sort_keys=True))
    #print('')
    
    for i in range(len(itemLabels)): 
        if itemLabels[i] in response["responses"][0]['webDetection']['bestGuessLabels'][0]['label']:
            print('Match found: ' + itemLabels[i])



def main():
    DOOR = 27
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    #service = authenticate()
    authenticate()
    scale = initScale()
    
    try:
        while True:
            while True:# (GPIO.input(DOOR) == 1):
                print("Door is closed")
                time.sleep(1)

                if True:# (GPIO.input(DOOR) == 0):
                    print("Door was opened")
                    
                    while False:# (GPIO.input(DOOR) == 0):
                        print("Waiting for door to close")
                        time.sleep(1)          
                    print("Door was closed")
                    
                    getWeight(scale)
                    #filename = getImage()
                    #response = detect(service, 'grannysmith.png')
                    #parse(response)
            print('Door is open, please close')
    
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()


if __name__ == '__main__':
    main()
