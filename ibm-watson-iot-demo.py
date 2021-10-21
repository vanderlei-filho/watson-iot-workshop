#!/usr/bin/python

import json
import signal
import getopt
import sys
import time
import random
import ibmiotf.device
#from piweathershield import PiWeatherShield


def interruptHandler(signal, frame):
	client.disconnect()
	sys.exit(0)

def usage():
	print(
		'TESS-IBM-Demo: Publish sensors data from TE Raspberry Pi Weather Shield to the IBM Internet of Things Foundation.' + '\n' +
		'\n' +
		'Usage: ' + '\n' +
		'  python tess-ibm-demo.py -c deviceConfigurationFile' + '\n' +
		'\n' +
		'Options: ' + '\n' +
		'  -h, --help       Display help information' + '\n' +
		'  -c, --config     Specify device configuration file' + '\n' +
		'  -v, --verbose    Be more verbose'
	)

def getSensorsJSON(verbose=False):
	#htu21d_humidity = weatherShield.htu21d.read_humidity()
	#htu21d_temperature = weatherShield.htu21d.read_temperature()
	#(ms5637_temperature, ms5637_pressure) = weatherShield.ms5637.read_temperature_and_pressure()
	#tsys01_temperature = weatherShield.tsys01.read_temperature()
	#(tsd305_temperature, tsd305_object_temperature) = weatherShield.tsd305.read_temperature_and_object_temperature()

	htu21d_humidity = random.uniform(10.5, 75.5)
	htu21d_temperature = random.uniform(22.1, 33.3)
	(ms5637_temperature, ms5637_pressure) = (random.uniform(22.1, 33.5), random.uniform(0.9, 2))
	tsys01_temperature = random.uniform(12.1, 53.3)
	(tsd305_temperature, tsd305_object_temperature) = (random.uniform(42.1, 13.5), random.uniform(1.9, 4))

	data = {
		'htu21d': {
			'humidity' : htu21d_humidity,
			'temperature' : htu21d_temperature
		},
		'ms5637': {
			'pressure' : ms5637_pressure,
			'temperature' : ms5637_temperature
		},
		'tsys01': {
			'temperature' : tsys01_temperature
		},
		'tsd305': {
			'temperature' : tsd305_temperature,
			'object_temperature' : tsd305_object_temperature
		}
	}
	if verbose:
		print('getSensorsJSON: {}'.format(data))
	return data

if __name__ == "__main__":
	signal.signal(signal.SIGINT, interruptHandler)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hn:vo:c:", ["help", "verbose", "config="])
	except getopt.GetoptError as err:
		print(str(err))
		usage()
		sys.exit(2)

	verbose = False
	deviceFile = None

	for o, a in opts:
		if o in ("-v", "--verbose"):
			verbose = True
		elif o in ("-c", "--cfg"):
			deviceFile = a
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		else:
			assert False, "unhandled option" + o

	if deviceFile == None:
		usage()
		sys.exit(2)

	# Initialize the device client.
	print('Connecting to IBM IoT... ')
	try:
		options = ibmiotf.device.ParseConfigFile(deviceFile)
		if verbose:
			print('options: {}'.format(options))
		client = ibmiotf.device.Client(options)
		client.connect()
	except Exception as e:
		print('\nCaught exception connecting device: {}'.format(str(e)))
		sys.exit()

	# Initialize Raspberry Pi Weather Shield
	#weatherShield = PiWeatherShield()

	# Now run main loop
	print('Running measurement loop, pushing sensors data every seconds...')
	print('(Press Ctrl+C to disconnect)')

	while(1):
		time.sleep(1)
		client.publishEvent('piweathershield', 'json', getSensorsJSON(verbose) , qos=0)
