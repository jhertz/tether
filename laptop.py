import tornado.web
import tornado.ioloop
import tornado.websocket
import subprocess
import os

SERVER_IP = "169.254.134.89"
SERVER_PORT = 6354



#subprocess.call("ifconfig tun0 10.0.0.1 10.0.0.1 netmask 255.255.255.0 up", shell=True)
#subprocess.call("route delete default; sudo route add default 10.0.0.1", shell=True)


class MainWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print "WebSocket opened"

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print "WebSocket closed"
        
    def allow_draft76():
        return True;
    


if __name__ == "__main__":
    print("hi")
    subprocess.call("/sbin/ifconfig en1 inet 169.254.134.89 netmask 255.255.0.0 alias", shell=True)
    tunFD = os.open("/dev/tun0", os.O_RDWR)
    application = tornado.web.Application([ (r"/", MainWebSocketHandler), ])
    application.listen(SERVER_PORT, address=SERVER_IP)
    tornado.ioloop.IOLoop.instance().start()
