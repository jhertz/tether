# -*- coding: iso-8859-1 -*-

import os
import sys
sys.path.append('tornado-2.2.1/')

import tornado.web
import tornado.ioloop

SERVER_PORT = 80

class ServerHandler(tornado.web.RequestHandler):
	def get(self):
		f = open('webapp.html', 'r')
		for line in f:
			self.write(line)
		f.close()

def mainLoop():
	print "CHECKPOINT 1", "Listening on port", SERVER_PORT
	application = tornado.web.Application([ (r"/", ServerHandler) ] )
	application.listen(SERVER_PORT)
	tornado.ioloop.IOLoop.instance().start()

mainLoop()