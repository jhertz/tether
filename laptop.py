######
# CS168 Final Project: Tether
# Laptop Component
# Must be run as root
# @author: jhertz
######

from tornado.web import *
from tornado.ioloop import *
import tornado.ioloop
from tornado.websocket import *
from subprocess import call
import os
import threading

SERVER_IP = "169.254.134.89"
SERVER_PORT = 6354
BUFFER_SIZE = 1024


tunFD = None





class MainWebSocketHandler(WebSocketHandler):
    def open(self):
        print "WebSocket opened"

    def on_message(self, message):
        #actual code goes here...
        #After binding, the server should listen for new websocket connections, then manage reading and
        #writing to these websockets.
        self.write_message(u"You said: " + message)

    def on_close(self):
        print "WebSocket closed"
        
    def allow_draft76(self):
        return True
    


class TunThread( threading.Thread):
   def run(self):
       while(True):
           data = os.read(tunFD, BUFFER_SIZE)
           print("got some data")


if __name__ == "__main__":
    print("LaptopTetherServer Starting!")
    application = Application([ (r"/", MainWebSocketHandler), ])
    #application.listen(SERVER_PORT, address=SERVER_IP)
    application.listen(SERVER_PORT)
    #map SERVER_IP to us on the ad-hoc network
    call("/sbin/ifconfig en1 inet 169.254.134.89 netmask 255.255.0.0 alias", shell=True)
    # open tun device
    tunFD = os.open("/dev/tun0", os.O_RDWR)
    #assign tun to 10.0.0.1
    call("ifconfig tun0 10.0.0.1 10.0.0.1 netmask 255.255.255.0 up", shell=True)
    #modify the routing table to send EVERYTHING through TUN
    call("route delete default; sudo route add default 10.0.0.1", shell=True)
    TunThread().start()
    IOLoop.instance().start()

    
