
from http.server import BaseHTTPRequestHandler, HTTPServer
import prctl
from socketserver import ThreadingMixIn
import threading
from . import configuration
from . import private
from base64 import b64decode
import os,sys,json

import io,gzip,re

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

    def user_authorized(self):
        try:
            return self._user_authorized()
        except Exception as e:
            raise
            print(str(e))
            return False

    def _user_authorized(self):
        if "Authorization" not in self.headers:
            return False
        auth = self.headers['Authorization']
        a_type, b64 = auth.split(' ')
        if a_type.lower() != 'basic':
            return False
        user, passwd = b64decode(b64).decode('utf8').split(':')
        if passwd == private.password:
            return True
        return False


    def do_GET(self):

        path,params,args = self._parse_url()

        if not self.user_authorized():
            self.send_response(401)
            self.send_header('WWW-Authenticate','Basic')
            self.end_headers()
            return

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

            obj = {'int_temp':self.server.app.stats.int_temp,
                'int_temp_min':self.server.app.stats.int_temp_min,
                'int_temp_max':self.server.app.stats.int_temp_max,
                'ext_temp':self.server.app.stats.ext_temp,
                'ext_temp_min':self.server.app.stats.ext_temp_min,
                'ext_temp_max':self.server.app.stats.ext_temp_max,
                'int_hygro':self.server.app.stats.int_hygro,
                'int_hygro_min':self.server.app.stats.int_hygro_min,
                'int_hygro_max':self.server.app.stats.int_hygro_max,
                'ext_hygro':self.server.app.stats.ext_hygro,
                'ext_hygro_min':self.server.app.stats.ext_hygro_min,
                'ext_hygro_max':self.server.app.stats.ext_hygro_max,
                'fan_status':self.server.app.logic.fan,
                'heater_status':self.server.app.logic.heat,
                'dehum_status':self.server.app.logic.dehum,
                'fan_force':self.server.app.buttons.fan,
                'heater_force':self.server.app.buttons.heater,
                'dehum_force':self.server.app.buttons.dehum,
                'fan_energy':self.server.app.stats.fan_energy,
                'fan_price':round(self.server.app.stats.fan_energy *
                    configuration.rate, 0),
                'heater_energy':self.server.app.stats.heater_energy,
                'heater_price':round(self.server.app.stats.heater_energy *
                    configuration.rate, 0),
                'dehum_energy':self.server.app.stats.dehum_energy,
                'dehum_price':round(self.server.app.stats.dehum_energy *
                    configuration.rate, 0)}

            self.wfile.write(
                json.dumps(obj).encode()
            )
            return

        elif path == 'api/reset':
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Cache-Control','no-cache, no-store, must-revalidate')
            self.send_header('Pragma','no-cache')
            self.send_header('Expires','0')
            self.end_headers()
            self.server.app.stats.reset_hygro_temp()
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
        if path.endswith('woff'):
            content = data
            self.send_header('Content-Encoding','identity')
            self.send_header('Content-Type', 'font/woff')
        elif path.endswith('woff2'):
            content = data
            self.send_header('Content-Encoding','identity')
            self.send_header('Content-Type', 'font/woff2')
        else:
            content = gzip.compress(data)
            self.send_header('Content-Encoding','gzip')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()

 #       print("serving",realpath)
        self.wfile.write(content)
        self.wfile.flush()

class CtahrWebServer(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        prctl.set_name('WebServer')
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
