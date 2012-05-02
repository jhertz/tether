# -*- coding: iso-8859-1 -*-

import base64

import sys
sys.path.append('tornado-2.2.1/')

import tornado.web
import tornado.ioloop
import tornado.websocket

AMAZON_IP = "10.190.122.124"
SERVER_PORT = 8080

class RedirectWebSocketHandler(tornado.websocket.WebSocketHandler):
	otherAddr = None
	
	def open(self):
		print "Redirect WebSocket opened"
	
	def on_message(self, message):
		print "Received message"
		
		#make a packet out of the message
		messageString = base64.b64decode(message)
		newPacket = IP(messageString)
		
		print "Packet Info:"
		print "src =", newPacket.src
		print "dst =", newPacket.dst
		print "len =", newPacket.len
		print "id =", newPacket.id
		
		#process the packet
		sendPacket = self.processPacket(newPacket)
		
		#send the packet out to the web
		responsePacket = sr1(sendPacket)
		
		if(responsePacket == None):
			print "NoneType"
		else:
			#send the response back
			self.sendPacketOnWebSocket(responsePacket)
	
	def on_close(self):
		print "Redirect WebSocket closed"
	
	def allow_draft76(self):
		return True
	
	#def __init__(self):
	#	self.otherAddr = None
	
	#if the otherAddr field has not been set yet, set with the packet field
	#replace the src address with the AMAZON_IP address
	#recalculate the checksum
	def processPacket(self, newPacket):
		#set otherAddr, if needed
		if(self.otherAddr == None):
			self.otherAddr = newPacket.src
		
		returnPacket = newPacket
		
		#replace the src of the packet
		returnPacket.src = AMAZON_IP
		
		#recalculate the checksum for the packet
		del returnPacket.chksum
		del returnPacket[TCP].chksum
		tempString = str(returnPacket)
		
		returnPacket = IP(tempString);
		
		return returnPacket
	
	#if received a packet from the web, send on the websocket
	#before sending, replace the dst address with otherAddr
	#then recalculate the checksum
	def sendPacketOnWebSocket(self, newPacket):
		sendPacket = newPacket
		
		#replace the dst of the packet
		if(self.otherAddr != None):
			sendPacket.dst = self.otherAddr
		
		#recalculate the checksum for the packet
		del sendPacket.chksum
		del sendPacket[TCP].chksum
		tempString = str(sendPacket)
		
		sendString = base64.b64encode(tempString)
		
		#send the packet on the websocket
		self.write_message(sendString)

def mainLoop():
	print "AMAZON SERVER: Listening on port", SERVER_PORT
	application = tornado.web.Application([ (r"/", RedirectWebSocketHandler), ])
	application.listen(SERVER_PORT)
	tornado.ioloop.IOLoop.instance().start()

mainLoop()