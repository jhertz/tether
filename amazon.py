# -*- coding: iso-8859-1 -*-

import tornado.web
import tornado.ioloop
import tornado.websocket

AMAZON_IP = "10.190.122.124"

class RedirectWebSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print "Redirect WebSocket opened"
	
	def on_message(self, message):
		#received a new message, print out
		print message
		
		#make a packet out of the message
		newPacket = IP(message)
		
		#process the packet
		sendPacket = processPacket(newPacket)
		
		#send the packet out to the web
		responsePacket = sr(sendPacket)
		
		#send the response back
		sendPacketOnWebSocket(responsePacket)
	
	def on_close(self):
		print "Redirect WebSocket closed"
	
	def allow_draft76():
		return True
	
	def __init__(self):
		self.otherAddr = None
	
	#if the otherAddr field has not been set yet, set with the packet field
	#replace the src address with the AMAZON_IP address
	#recalculate the checksum
	def processPacket(newPacket):
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
		
		return IP(tempString)
	
	#if received a packet from the web, send on the websocket
	#before sending, replace the dst address with otherAddr
	#then recalculate the checksum
	def sendPacketOnWebSocket(newPacket):
		sendPacket = newPacket
		
		#replace the dst of the packet
		if(self.otherAddr != None):
			sendPacket.dst = self.otherAddr
		
		#recalculate the checksum for the packet
		del sendPacket.chksum
		del sendPacket[TCP].chksum
		tempString = str(sendPacket)
		
		#send the packet on the websocket
		self.write_message(tempString)

def mainLoop():
	application = tornado.web.Application([ (r"/", RedirectWebSocketHandler), ])
	application.listen(SERVER_PORT, address=SERVER_IP)
	tornado.ioloop.IOLoop.instance().start()

mainLoop()