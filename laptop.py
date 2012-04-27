from tornado.web import *
from tornado.ioloop import *
import tornado.ioloop
from tornado.websocket import *
from subprocess import *
import os

SERVER_IP = "169.254.134.89"
SERVER_PORT = 6354


tunFD = None



def tunRead(self):
    data = read(tunFD)
    print("read some data from tun")
    return

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
        return True;
    
    def initialize(self):
        return

   


if __name__ == "__main__":
    print("LaptopTetherServer Starting!")
    application = Application([ (r"/", MainWebSocketHandler), ])
    application.listen(SERVER_PORT, address=SERVER_IP)
    application.listen(SERVER_PORT)
    call("/sbin/ifconfig en1 inet 169.254.134.89 netmask 255.255.0.0 alias", shell=True)
    tunFD = os.open("/dev/tun0", os.O_RDWR)
    call("ifconfig tun0 10.0.0.1 10.0.0.1 netmask 255.255.255.0 up", shell=True)
    call("route delete default; sudo route add default 10.0.0.1", shell=True)
    ioLoop = IOLoop.instance()
    ioLoop.start()
    ioLoop.add_handler(tunFD, tunRead, events=ioLoop.READ )

    
