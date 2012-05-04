# -*- coding: iso-8859-1 -*-

import base64
import subprocess
import threading

import sys
sys.path.append('tornado-2.2.1/')

import tornado.web
import tornado.ioloop
import tornado.websocket

AMAZON_IP = "10.190.122.124"
BROWN_IP = "138.16.160.4"
SERVER_PORT = 8080

webSocket = None

class RedirectWebSocketHandler(tornado.websocket.WebSocketHandler):
	otherAddr = None
	nextAddr = None
	
	def open(self):
		print "Redirect WebSocket opened"
		global webSocket
		webSocket = self
	
	def on_message(self, message):
		#make a packet out of the message
		messageString = base64.b64decode(message)
		newPacket = IP(messageString)
		
		if self.nextAddr == None:
			self.nextAddr = []
		if not newPacket.dst in self.nextAddr:
			self.nextAddr.append(newPacket.dst)
		
		print "ON MESSAGE src=", newPacket.src, "dst=", newPacket.dst, "len=", newPacket.len
		
		#process the packet
		sendPacket = self.processPacket(newPacket)
		
		print "SENDING src=", sendPacket.src, "dst=", sendPacket.dst, "len=", sendPacket.len
		
		#send the packet out to the web
		send(sendPacket)
	
	def on_close(self):
		print "Redirect WebSocket closed"
		global webSocket
		webSocket = None
	
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
		if self.nextAddr == None:
			print "NONE!!!!"
		elif not newPacket.src in self.nextAddr:
			print "self.nextAddr=", self.nextAddr
			print "IGNORING src=", newPacket.src, "dst=", newPacket.dst, "len=", newPacket.len
		else:
			sendPacket = newPacket
			
			#replace the dst of the packet
			if(self.otherAddr != None):
				sendPacket.dst = self.otherAddr
			
			#recalculate the checksum for the packet
			del sendPacket.chksum
			del sendPacket[TCP].chksum
			tempString = str(sendPacket)
			tempPacket = IP(tempString)
			
			sendString = base64.b64encode(tempString)
			
			#send the packet on the websocket
			print "SENDING SOMETHING ON WIRE src=", tempPacket.src, "dst=", tempPacket.dst, "len=", tempPacket.len
			self.write_message(sendString)

class SniffThread(threading.Thread):
	def run(self):
		global webSocket
		
		while(True):
			incoming = sniff(iface="eth0", count=1)
			newPacket = incoming[0]
			
			if webSocket != None:
				if webSocket.otherAddr != None:
					if newPacket.haslayer(IP):
						newPacket = newPacket[IP]
						
						if newPacket.src == BROWN_IP:
							continue
						
						print "Received: src=", newPacket.src, "dst=", newPacket.dst, "len=", newPacket.len
						webSocket.sendPacketOnWebSocket(newPacket)
			
			#if webSocket != None and webSocket.otherAddr != None:

def mainLoop():
	command = "sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP"
	print command
	subprocess.call(command, shell=True)
	print "AMAZON SERVER: Listening on port", SERVER_PORT
	application = tornado.web.Application([ (r"/", RedirectWebSocketHandler), ])
	application.listen(SERVER_PORT)
	
	sniffThread = SniffThread()
	sniffThread.start()
	
	tornado.ioloop.IOLoop.instance().start()

mainLoop()