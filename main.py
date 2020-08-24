from flask import Flask, render_template
from zeroconf import Zeroconf, ServiceBrowser
import urllib, json

app = Flask(__name__)

servers = {}

class MyListener:
    def add_service(self, zc, type, name):
        info = zc.get_service_info(type, name)

        hexaddress = info.addresses[0]

        servers[name] = {
            "address": "{}.{}.{}.{}".format(hexaddress[0], hexaddress[1],hexaddress[2],hexaddress[3]),
            "name": info.server.split('.')[0],
            "port": info.port,
            "type": info.type,
            "raw": info
        }
        print("Service %s added, service info: %s" % (name, info))
        
    def remove_service(self, zeroconf, type, name):
        del servers[name]

    def update_service(self, zeroconf, type, name):
    pass

def getJson(url):
    operUrl = urllib.request.urlopen(url)
    if(operUrl.getcode()==200):
       data = operUrl.read()
       jsonData = json.loads(data)
    else:
       print("Error receiving data", operUrl.getcode())
    return jsonData

@app.route('/')
def index():
    newServers = {}
    for name,server in servers.items():
        hardware = None
        software = None
        platform = None

        if server["type"] == "_pimonitor._tcp.local.":
            hardware = getJson("http://{}:{}/v1/hardware".format(server["address"], server["port"]))
            software = getJson("http://{}:{}/v1/software".format(server["address"], server["port"]))
            platform = getJson("http://{}:{}/v1/platform".format(server["address"], server["port"]))
            thisServer = {}
            thisServer["info"] = server
            thisServer["hardware"] = hardware
            thisServer["software"] = software
            thisServer["platform"] = platform
            newServers[name] = thisServer
            
        elif server["type"] == "_blackmagic._tcp.local.":
            thisServer = {}
            hardware = {
              "_hostname": server["raw"].name.split('.')[0],
              "model": server["raw"].properties[b"name"].decode('utf-8')
            }
            software = {
              "version": server["raw"].properties[b"release version"].decode('utf-8')
            }
            platform = {
              "platform": "pager"
            }
            thisServer["info"] = server
            thisServer["hardware"] = hardware
            thisServer["software"] = software
            thisServer["platform"] = platform
            newServers[name] = thisServer
    


    return render_template('main.j2', servers=newServers)


if __name__ == '__main__':
    zeroconf = Zeroconf()
    listener = MyListener()
    browser = ServiceBrowser(zeroconf, "_pimonitor._tcp.local.", listener)
    browser2 = ServiceBrowser(zeroconf, "_blackmagic._tcp.local.", listener)
    app.run(debug=True, host="0.0.0.0")