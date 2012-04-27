import tornado.web
import subprocess

print("hi")
subprocess.call("/sbin/ifconfig en1 inet 169.254.134.89 netmask 255.255.0.0 alias", shell=True)
