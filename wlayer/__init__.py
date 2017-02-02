#example: /warra$ python -m warra.server localhost 1234
'''
import wlay.layouts as l
import wlay as w
w.setBasePath("./wlay/presets/")
'''
__version__ = '0.0.1'
import logging
import glob
import sys
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(process)d %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


server = "--not-set--"

current_windows = []
definitions = {}

def getBasePath():
	
	return path


def setBasePath(inpath):
	global definitions, path
	
	path = inpath
	defsPath =path.rstrip("/") + "/*.defs.json"
	for defsPath in glob.glob(defsPath):
		defs = json.loads(open(defsPath).read())
		for window in defs.keys():
			definitions[window] = defs[window]


	definitions = json.loads(open(defsPath).read())


def getServerAddress():
	global server
	return server

def setServerAddress(address, port=80, static_uri='static'):
	global server
	if port != 80:
		server = "http://{0}:{1}/{2}/".format(address, port, static_uri.strip("/"))
	else:
		server = "http://{0}/{2}/".format(address, static_uri.strip("/"))