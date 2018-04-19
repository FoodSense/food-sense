import time
import sys

try:
    from picamera import PiCamera
    import RPi.GPIO as GPIO
except ImportError:
    print('Failed to import required Detect class modules')
    sys.exit(1)

try:
    LED = 27
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED, GPIO.OUT)
    
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
        camera.hflip = True
        camera.vflip = True
        camera.crop = (0.0, 0.0, 1.0, 1.0)

        GPIO.output(LED, True)
        camera.start_preview()

        while True:
            continue
        
except KeyboardInterrupt:
    print('Progarm terminated')
    GPIO.output(LED, False)
    GPIO.cleanup
    sys.exit()
