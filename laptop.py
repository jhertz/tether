######
# CS168 Final Project: Tether
# Laptop Component
# Must be run as root
# @author: jhertz
######


#imports
from tornado.web import *
from tornado.ioloop import *
import tornado.ioloop
from tornado.websocket import *
from subprocess import call
import os
import threading
import sys
from websocket import create_connection

#constants
SERVER_IP = "169.254.134.89"
SERVER_PORT = 6354
BUFFER_SIZE = 1024

#DEBUG FLAGS
D_TUN = False
D_WEB = False
D_CLIENT = True


#globals
tunFD = None
theWebSocket = None


#the WebSocket handler
class MainWebSocketHandler(WebSocketHandler):
    def open(self):
        #After binding, the server should listen for new websocket connections, then manage reading and
        #writing to these websockets.
        if(theWebSocket != None):
            print "there is already a connection open"
            sys.exit(1)
        theWebSocket = self
        print "WebSocket opened"

    def on_message(self, message):
        #okay, we got some data off the websocket, we need to pipe it into the TUN device
        os.write(tunFD, message)

    def on_close(self):
        theWebSocket = None
        print "WebSocket closed"
        
    def allow_draft76(self):
        return True
    
    def processTunData(self, data):
        self.write_message(message, binary=True) # might need to try binary = false 
        return
    



#the TUN thread, perpetually polls to see if there's new data on the TUN device
class TunThread( threading.Thread):
   def run(self):
       while(True):
           data = os.read(tunFD, BUFFER_SIZE)
           print("read some TUN data" , data)
           if(theWebSocket != None):
               theWebSocket.processTunData(data)



#main entry point
if __name__ == "__main__":
    print("LaptopTetherServer Starting!")
    
    if(D_TUN):
        # open tun device
        tunFD = os.open("/dev/tun0", os.O_RDWR)
        #map SERVER_IP to us on the ad-hoc network
        call("/sbin/ifconfig en1 inet 169.254.134.89 netmask 255.255.0.0 alias", shell=True)
        #assign tun to 10.0.0.1
        call("ifconfig tun0 10.0.0.1 10.0.0.1 netmask 255.255.255.0 up", shell=True)
        #modify the routing table to send EVERYTHING through TUN
        call("route delete default; sudo route add default 10.0.0.1", shell=True)
        TunThread().start()
    

    if(D_WEB):
        #application = Application([ (r"/", MainWebSocketHandler), ])
        #application.listen(SERVER_PORT, address=SERVER_IP) #application.listen(SERVER_PORT)  
        IOLoop.instance().start() #this call blocks, so it must be made last...


ws = create_connection("ws://ec2-50-19-32-33.compute-1.amazonaws.com:8080/")
print "Sending 'Hello, World'..."
ws.send("Hello, World")
print "Sent"
print "Reeiving..."
result =  ws.recv()
print "Received '%s'" % result
ws.close()
        
