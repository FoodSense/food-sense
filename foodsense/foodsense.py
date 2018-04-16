import sys
import time

try:
	from detect import Detect
	from firebase import Firebase
	from monitoring import Monitoring
	from scale import Scale
except ImportError:
	print('Failed to import required Food Sense modules')
	sys.exit(1)

# Entrypoint
def foodSense():
	print('Starting Food Sense')

	# Begin initializing necessary components
	fb = Firebase()
	det = Detect(fb)
	mon = Monitoring()
	sc = Scale()

	# Set scale calibration
	sc.setReferenceUnit(-25.725)
	sc.reset()
	sc.tare()

	### START DEBUG ###
	### END DEBUG ###

	### MAIN LOOP ###
	while True:
		while mon.powerOn:
			print('Power is on')
			time.sleep(1)

			while mon.doorClosed():
				print('Door is closed')
				time.sleep(1)

				if mon.doorOpen():
					print('Door was opened')

					while mon.doorOpen():
						print('Waiting for door to close')
						time.sleep(1)
					print('Door is closed again')

					sc.getWeight()
					det.getImage()
					det.detectItem()

					if sc.weight < sc.prevWeight:
						det.parseResponse(True, sc.weight)
					elif sc.weight > sc.prevWeight:
						det.parseResponse(False)
					else:
						print('Error determining weight')
			else:
				print('Door must be closed on program startup')
		else:
			fb.powerWarning()
			while mon.powerOn() is False:
				if mon.checkTemp():
					fb.tempWarning()
	### END MAIN LOOP ###
	
# Make foodSense() the default entry point
if __name__ == '__main__':
	foodSense()
