######
# CS168 Final Project: Tether
# Laptop Component
# Must be run as root on an OSX system
# @author: jhertz
# @requires: tornado
# @requires: TunTap
######


#imports
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from subprocess import call
from threading import Thread
import os
import base64

#constants
SERVER_IP = "169.254.134.89"
SERVER_PORT = 6354
BUFFER_SIZE = 10240




#the WebSocket handler
class MainWebSocketHandler(WebSocketHandler):
    
    #fields
    tunFD = None
    
    #methods:
    
    #opens the tun device, makes some syscalls, start the TUN polling thread
    def open(self):
        # open tun device
        tunFD = os.open("/dev/tun0", os.O_RDWR)
        self.tunFD = tunFD
        #assign tun to 10.0.0.1
        call("ifconfig tun0 10.0.0.1 10.0.0.1 netmask 255.255.255.0 up", shell=True)
        #modify the routing table to send EVERYTHING through TUN
        call("route delete default", shell=True)
        call("route add default 10.0.0.1", shell=True)
        #setup TUN thread and start it
        thread = Thread(target=tunTask, args=(self,tunFD))
        thread.start()
        print "WebSocket opened"
        
    #okay, we got some data off the websocket, we need to decode it, and pipe it into the TUN device
    def on_message(self, message):
        #print "got message from server"
        decodedData = base64.b64decode(message)
        os.write(self.tunFD, decodedData)
   

    #called on close
    def on_close(self):
        theWebSocket = None
        print "WebSocket closed"
        
    def allow_draft76(self):
        return True
    
    #encode the data and write it to the websockets
    def processTunData(self, data):
        encodedData = base64.b64encode(data)
        #print "writing data from TUN to websocket"
        self.write_message(encodedData) 
        return
    



#the TUN thread, perpetually polls to see if there's new data on the TUN device
def tunTask(webSocket, tunFD):
       while(True):
           data = os.read(tunFD, BUFFER_SIZE)
          #print("read some TUN data" , data)
           webSocket.processTunData(data)



#main entry point
if __name__ == "__main__":
    print("LaptopTetherServer Starting!\n")
     #map SERVER_IP to us on the ad-hoc network
    call("/sbin/ifconfig en1 inet 169.254.134.89 netmask 255.255.0.0 alias", shell=True)
    application = Application([ (r"/", MainWebSocketHandler), ])
    application.listen(SERVER_PORT)  #binding to the port worked fine, we didn't need to bind to the address too
    IOLoop.instance().start() #this call blocks, so it must be made last...