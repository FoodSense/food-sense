import sys
import time

try:
	from detect import Detect
	from monitoring import Monitoring
	from scale import Scale
except ImportError:
	print('Failed to import required Food Sense modules')
	sys.exit(1)

# Entrypoint
def foodSense():
	print('Starting Food Sense')

	# Begin initializing necessary components)
	detect = Detect()
    monitor = Monitoring()
	scale = Scale()

	# Set scale calibration
	scale.setReferenceUnit(-25.725)
	scale.reset()
	scale.tare()

	### START DEBUG ###
    ### END DEBUG ###

	### MAIN LOOP ###
	while True:
		while monitor.powerOn:
			print('Power is on')
			time.sleep(1)

			while monitor.doorClosed():
				print('Door is closed')
                monitor.checkTemp():
                time.sleep(1)

                if monitor.doorOpen():
					print('Door was opened')
                    monitor.startTimer()

					while monitor.doorOpen():
						print('Waiting for door to close')
                        monitor.checkTimer()
                        monitor.checkTemp()
                        time.sleep(1)
                    else:
                        print('Door was closed')

					    scale.getWeight()
					    detect.getImage()
					    detect.detectItem()
						detect.parseResponse(scale.weight)
            else:
				print('Door must be closed on program startup')
        else:
            monitor.powerSave()
    else:
        pass
	### END MAIN LOOP ###
	
# Make foodSense() the default entry point
if __name__ == '__main__':
	foodSense()
