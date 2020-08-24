from zeroconf import ServiceBrowser, Zeroconf
import time

class MyListener:
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))

zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_pimonitor._tcp.local.", listener)


while True:
    time.sleep(0.5)
