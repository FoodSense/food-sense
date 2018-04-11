import sys
import time
from picamera import PiCamera
import RPi.GPIO as GPIO

# GPIO pins
DOOR = 5
LED = 27
POWER = 6

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DOOR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED, GPIO.OUT)

with PiCamera() as camera:
    camera.sharpness = 0
    camera.contrast = 50
    camera.brightness = 50
    camera.saturation = 0
    camera.ISO = 0
    camera.exposure_compensation = True
    camera.exposure_mode = 'auto'
    camera.awb_mode = 'auto'
    camera.image_effect = 'none'
    camera.color_effects = None
    camera.rotation = 180
    camera.hflip = False
    camera.vflip = False
    camera.crop = (0.0, 0.0, 1.0, 1.0)
 
    try:
        GPIO.output(LED, 1)
        camera.start_preview()
                
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.output(LED, 0)
        sys.exit()
