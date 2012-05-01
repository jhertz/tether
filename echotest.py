# -*- coding: iso-8859-1 -*-

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
		tempString = str(message)
		tempPacket = IP(tempString)
		print "version =", tempPacket.version
		print "id =", tempPacket.id
		print "proto =", tempPacket.proto
		print "src =", tempPacket.src
		print "dst =", tempPacket.dst
		print "len =", tempPacket.len
		print "recv:", str(tempPacket)
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