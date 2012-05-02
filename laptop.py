######
# CS168 Final Project: Tether
# Laptop Component
# Must be run as root
# @author: jhertz
# @requires: tornado
######


#imports
from tornado.web import Application
from tornado.ioloop import IOLoop
import tornado.ioloop
from tornado.websocket import WebSocketHandler
from subprocess import call
import os
from threading import Thread
import base64
#constants
SERVER_IP = "169.254.134.89"
SERVER_PORT = 6354
BUFFER_SIZE = 1024




#the WebSocket handler
class MainWebSocketHandler(WebSocketHandler):
    def open(self):
        # open tun device
        tunFD = os.open("/dev/tun0", os.O_RDWR)
        #assign tun to 10.0.0.1
        call("ifconfig tun0 10.0.0.1 10.0.0.1 netmask 255.255.255.0 up", shell=True)
        #modify the routing table to send EVERYTHING through TUN
        call("route delete default", shell=True)
        call("route add default 10.0.0.1", shell=True)
        #setup TUN thread and start it
        thread = Thread(target=tunTask, args=(self,tunFD))
        thread.start()
        print "WebSocket opened"
        

    def on_message(self, message):
        #okay, we got some data off the websocket, we need to pipe it into the TUN device
       # os.write(tunFD, message)
       #print "got message:" , message
       #self.write_message(message)
       return
   
   

    def on_close(self):
        theWebSocket = None
        print "WebSocket closed"
        
    def allow_draft76(self):
        return True
    
    def processTunData(self, data):
        encodedData = base64.b64encode(data)
        print "writing data from TUN to websocket"
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
    #application.listen(SERVER_PORT, address=SERVER_IP) 
    application.listen(SERVER_PORT)  
    IOLoop.instance().start() #this call blocks, so it must be made last...
    

   
        
