
import threading,time,os
import json
import configuration

class CtahrStats(threading.Thread):
    daemon = True

    def __init__(self, app):
        threading.Thread.__init__(self)
        print "[+] Starting Stats module"
        self.app = app
        self.lock = threading.Lock()
        self.running = True
        self.data = ({'int':{'temp':{'min':None, 'max':None},
            'hygro':{'min':None, 'max':None}},
            'ext':{'temp':{'min':None, 'max':None},
            'hygro':{'min':None, 'max':None}}})

        self.reset_hygro_temp()
        self.log_time = time.time()
        self.get_from_file()


    def get_from_file(self):
        if os.path.isfile(configuration.stats_log_file):
            with open(configuration.stats_log_file, 'r') as f:
                try:
                    self.data = json.load(f)
            with self.lock:
                self.int_hygro_max = self.data['int']['hygro']['max']
                self.int_hygro_min = self.data['int']['hygro']['min']
                self.int_temp_max = self.data['int']['temp']['max']
                self.int_temp_min = self.data['int']['temp']['min']
                self.ext_hygro_max = self.data['ext']['hygro']['max']
                self.ext_hygro_min = self.data['ext']['hygro']['min']
                self.ext_temp_max = self.data['ext']['temp']['max']
                self.ext_temp_min = self.data['ext']['temp']['min']


    def save_to_file(self):
        with self.lock:
            self.data['int']['hygro']['max'] = self.int_hygro_max
            self.data['int']['hygro']['min'] = self.int_hygro_min
            self.data['int']['temp']['max'] = self.int_temp_max
            self.data['int']['temp']['min'] = self.int_temp_min
            self.data['ext']['hygro']['max'] = self.ext_hygro_max
            self.data['ext']['hygro']['min'] = self.ext_hygro_min
            self.data['ext']['temp']['max'] = self.ext_temp_max
            self.data['ext']['temp']['min'] = self.ext_temp_min
        with open(configuration.stats_log_file, 'w') as f:
            json.dump(self.data, f)


    def update_values(self):
        int_values = self.app.thermohygro_interior.get()
        ext_values = self.app.thermohygro_exterior.get()
        if int_values != None and ext_values != None:
            with self.lock:
                self.int_hygro, self.int_temp, int_time = int_values
                self.ext_hygro, self.ext_temp, ext_time = ext_values
            return True
        else:
            return False


    def reset_hygro_temp(self):
        while not self.update_values():
            time.sleep(0.5)
        with self.lock:
            self.int_hygro_max = self.int_hygro
            self.int_hygro_min = self.int_hygro
            self.int_temp_max = self.int_temp
            self.int_temp_min = self.int_temp
            self.ext_hygro_max = self.ext_hygro
            self.ext_hygro_min = self.ext_hygro
            self.ext_temp_max = self.ext_temp
            self.ext_temp_min = self.ext_temp



    def do_math(self):
        with self.lock:
            # Interior hygrometry
            if self.int_hygro > self.int_hygro_max:
                self.int_hygro_max = self.int_hygro
            elif self.int_hygro < self.int_hygro_min:
                self.int_hygro_min = self.int_hygro

            # Interior temperature
            if self.int_temp > self.int_temp_max:
                self.int_temp_max = self.int_temp
            elif self.int_temp < self.int_temp_min:
                self.int_temp_min = self.int_temp

            # Exterior hygrometry
            if self.ext_hygro > self.ext_hygro_max:
                self.ext_hygro_max = self.ext_hygro
            elif self.ext_hygro < self.ext_hygro_min:
                self.ext_hygro_min = self.ext_hygro

            # Exterior temperature
            if self.ext_temp > self.ext_temp_max:
                self.ext_temp_max = self.ext_temp
            elif self.ext_temp < self.ext_temp_min:
                self.ext_temp_min = self.ext_temp

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            if self.update_values():
                self.do_math()
            if (time.time() - self.log_time) > 10:
                self.save_to_file()
            time.sleep(1)
        print "[-] Stoping Stats module"
