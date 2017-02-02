
import sys
import os
import time
import signal
import logging

from wserver import Server
from wserver import getArgs

from tornado.web import RequestHandler
from tornado.ioloop import IOLoop


from . import logger
from . import getBasePath
from . import setBasePath
from . import setServerAddress



class Ping(RequestHandler):
	def get(self):
		self.write({'ping': 'pong'})

	def post(self):
		args = getArgs(self)
		#pprint.pprint(args)
		self.write(args)

def handleSigTERM(x,y):
	print "SIGTERM"
	quit()

def handleSigINT(x,y):
	print "SIGINT"
	quit()


def quit():
	global run_flag
	run_flag = False
	IOLoop.instance().stop()
# python example.py localhost 1234
# curl localhost:1234

if __name__ == '__main__':
	global run_flag

	signal.signal(signal.SIGTERM, handleSigTERM)
	signal.signal(signal.SIGHUP, handleSigTERM)
	signal.signal(signal.SIGINT, handleSigINT)


	address = sys.argv[1]
	port = int(sys.argv[2])

	try:
		setBasePath(sys.argv[3])
	except:
		pass

	staticpath = getBasePath()

	if os.path.exists(staticpath) == False:
		os.mkdir(staticpath)

	static_uri='/static'
	setServerAddress(address, port, static_uri)
	server = Server(
		port=port,
		address=address,
		static_uri=static_uri,
		static_path=staticpath
		)
	server.daemon=True

	server.addResource((r"/ping", Ping))

	print "pid %d" %os.getpid()
	logger.info("pid %d" %os.getpid())

	server.start()

	
	run_flag = True
	while run_flag:
		time.sleep(1)
	
	if run_flag == False:
		server.quit()

	server.join()


