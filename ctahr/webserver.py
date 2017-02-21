
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
from . import configuration

import os,sys,json

import io, gzip

class MyHTTPServer(ThreadingMixIn,HTTPServer):
    pass

class MyRequestHandler(BaseHTTPRequestHandler):

    def _parse_url(self):
        # parse URL
        path = self.path.strip('/')
        sp = path.split('?')
        if len(sp) == 2:
            path, params = sp
        else:
            path, = sp
            params = None
        args = path.split('/')

        return path,params,args

    def log_message(self, format, *args):
        pass # nothing to do

    def do_GET(self):

        path,params,args = self._parse_url()

#        print(path,params,args)

        if ('..' in args) or ('.' in args):
            self.send_error(400, "A .. ? Really ?")
            self.end_headers()

        if path == '':
            path = 'index.html'

        if path == 'api/status':
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Cache-Control','no-cache, no-store, must-revalidate')
            self.send_header('Pragma','no-cache')
            self.send_header('Expires','0')
            self.end_headers()

            obj = {'int_temp':self.server.app.dummy.int_temp,
                'int_temp_min':self.server.app.dummy.int_temp_min,
                'int_temp_max':self.server.app.dummy.int_temp_min,
                'ext_temp':self.server.app.dummy.ext_temp,
                'ext_temp_min':self.server.app.dummy.ext_temp_min,
                'ext_temp_max':self.server.app.dummy.ext_temp_min,
                'int_hygro':self.server.app.dummy.int_hygro,
                'ext_hygro':self.server.app.dummy.ext_hygro,
                'fan_status':self.server.app.dummy.fan_status,
                'heater_status':self.server.app.dummy.heater_status,
                'dehum_status':self.server.app.dummy.dehum_status,
                'fan_energy':self.server.app.dummy.fan_energy,
                'heater_energy':self.server.app.dummy.heater_energy,
                'dehum_energy':self.server.app.dummy.dehum_energy}

            self.wfile.write(
                json.dumps(obj).encode()
            )
            return

        elif path == 'api/increase':
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Cache-Control','no-cache, no-store, must-revalidate')
            self.send_header('Pragma','no-cache')
            self.send_header('Expires','0')
            self.end_headers()
            self.server.app.dummy.increase()
            return

        elif path.startswith('api/data'):

            *rest,period = args

            period = int(period)

            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Cache-Control','no-cache, no-store, must-revalidate')
            self.send_header('Pragma','no-cache')
            self.send_header('Expires','0')

            # fetch file and compress it
            data = self.server.app.wrapper.get_rrd_json(period).encode('utf8')
            content = gzip.compress(data)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Content-Encoding','gzip')

            self.end_headers()

            self.wfile.write(content)
            return


        realpath = os.path.join('www',path)

        if not os.path.isfile(realpath):
            self.send_error(404, "File not found")
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('Cache-Control','public, max-age=86400')

        # fetch file and compress it
        data = open(realpath,'rb').read()
        content = gzip.compress(data)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Content-Encoding','gzip')
        self.end_headers()

 #       print("serving",realpath)
        self.wfile.write(content)
        self.wfile.flush()

class CtahrWebServer(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        print("[+] Starting webserver")
        self.app = app
        self.httpd = None

    def stop(self):
        if self.httpd is not None:
            self.httpd.shutdown()

    def run(self):
        self.httpd = MyHTTPServer(('', configuration.port), MyRequestHandler)
        self.httpd.app = self.app
        self.httpd.serve_forever()
        print("[-] Stopping webserver")
