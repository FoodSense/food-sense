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

	### START DEBUG ###

	det.timestamp = 'pop'
	det.filename = '../images/' + det.timestamp + '.jpg'
	det.detectItem()
	det.parseResponse()

	### END DEBUG ###

	### MAIN LOOP ###
	#while True:
		#while mon.powerOn():
			#while mon.doorClosed():
				#if mon.checkTemp():
					#fb.tempWarning()
				#if mon.doorOpen():
					#mon.startTimer()
					#while mon.doorOpen():
						#if mon.timerExceeded():
							#fb.doorWarning()
						#if mon.checkTemp():
							#fb.tempWarning()
					## weight, image, detect, parse, add/remove here
				#else:
					#pass
			#else:
				#print('Door must be closed on system start')
		#else:
			#fb.powerWarning()
			#while mon.powerOn() is False:
				#if mon.checkTemp():
					#fb.tempWarning()
	#else:
		#pass
	### END MAIN LOOP ###
	
# Make foodSense() the default entry point
if __name__ == '__main__':
	foodSense()
