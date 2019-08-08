#module for communication between the wattown pi and the substation pi

import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

WATTOWN_SERVER_SOCKET = '192.168.4.1:7301'
SUBSTATION_SERVER_SOCKET = '192.168.4.5:7302'

def sendCommand(socket, command):
    url = 'http://' + socket + '/' + command

    try:
        requests.get(url, timeout = 0.2)
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.ConnectionError:
        return True # python HTTP server causes connection error with requests module

def testConnection(socket):
    return sendCommand(socket, '')

class WebServer(threading.Thread):

    def __init__(self, requestHandler, port):
        self.requestHandler = requestHandler
        self.serverAddress = ('' , port)

        super().__init__()

    def run(self):
        self.server = HTTPServer(self.serverAddress, self.requestHandler)
        self.server.serve_forever()

    def join(self, timeout = None):         
        self.server.shutdown()
        threading.Thread.join(self, timeout)

class RequestHandler(BaseHTTPRequestHandler):
    def setHeaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers

    def getCommand(self):
        return self.path[1:]

    def do_GET(self):
        self.setHeaders()
        command = self.getCommand()
        self.handleCommand(command)
        self.wfile.write(bytes("<html><head></head><body>Hello World!</body></html>", 'utf-8'))

    def handleCommand(self, command):
        raise NotImplementedError

class WattownRequestHandler(RequestHandler):
    substationModeObj = None
    def handleCommand(self,command):
        if command == 'openSW1':
            self.substationModeObj.setSW1Closed(False)
        elif command == 'closeSW1':
            self.substationModeObj.setSW1Closed(True)

class SubstationRequestHandler(RequestHandler):
    def handleCommand(self, command):
        pass
