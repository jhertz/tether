# -*- coding: iso-8859-1 -*-

import base64

import sys
sys.path.append('tornado-2.2.1/')

import tornado.web
import tornado.ioloop
import tornado.websocket

SERVER_PORT = 8080

class EchoWebSocket(tornado.websocket.WebSocketHandler):
	def open(self):
		print "WebSocket opened"
	
	def on_message(self, message):
		tempString = base64.b64decode(message)
		tempPacket = IP(tempString)
		print "src =", tempPacket.src
		print "dst =", tempPacket.dst
		self.write_message(u"You said: " + message)
	
	def on_close(self):
		print "WebSocket closed"
	
	def allow_draft76(self):
		return True

def mainLoop():
	print "ECHOTEST:", "Listening on port", SERVER_PORT
	application = tornado.web.Application([ (r"/", EchoWebSocket), ])
	application.listen(SERVER_PORT)
	tornado.ioloop.IOLoop.instance().start()

mainLoop()