
from __future__ import division
import threading,time,os
import monotonic
import json
import configuration

class CtahrStats(threading.Thread):
    daemon = True

    def __init__(self, app):
        threading.Thread.__init__(self)
        print "[+] Starting stats module"
        self.app = app
        self.lock = threading.Lock()
        self.running = True
        self.heater_uptime = 0
        self.dehum_uptime = 0
        self.data = ({'int':{'temp':{'min':None, 'max':None},
            'hygro':{'min':None, 'max':None}},
            'ext':{'temp':{'min':None, 'max':None},
            'hygro':{'min':None, 'max':None}},
            'fan':{'energy':None, 'time':None},
            'heater':{'energy':None, 'time':None},
            'dehum':{'energy':None, 'time':None}})
        self.reset_hygro_temp()
        self.log_time = monotonic.time.time()
        self.get_from_file()


    def get_from_file(self):
        if os.path.isfile(configuration.stats_log_file):
            with open(configuration.stats_log_file, 'r') as f:
                try:
                    self.data = json.load(f)
                except:
                    pass
            with self.lock:
                self.int_hygro_max = self.data['int']['hygro']['max']
                self.int_hygro_min = self.data['int']['hygro']['min']
                self.int_temp_max = self.data['int']['temp']['max']
                self.int_temp_min = self.data['int']['temp']['min']
                self.ext_hygro_max = self.data['ext']['hygro']['max']
                self.ext_hygro_min = self.data['ext']['hygro']['min']
                self.ext_temp_max = self.data['ext']['temp']['max']
                self.ext_temp_min = self.data['ext']['temp']['min']
                self.fan_global_time = self.data['fan']['time']
                self.fan_energy = self.data['fan']['energy']
                self.heater_global_time = self.data['heater']['time']
                self.heater_energy = self.data['heater']['energy']
                self.dehum_global_time = self.data['dehum']['time']
                self.dehum_energy = self.data['dehum']['energy']


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
            self.data['fan']['time'] = self.fan_global_time
            self.data['fan']['energy'] = self.fan_energy
            self.data['heater']['time'] = self.heater_global_time
            self.data['heater']['energy'] = self.heater_energy
            self.data['dehum']['time'] = self.dehum_global_time
            self.data['dehum']['energy'] = self.dehum_energy
        with open(configuration.stats_log_file, 'w') as f:
            json.dump(self.data, f)


    def update_values(self):
        int_values = self.app.thermohygro_interior.get()
        ext_values = self.app.thermohygro_exterior.get()
        if int_values[3] != 0 and ext_values[3] != 0:
            with self.lock:
                self.int_hygro, self.int_temp = int_values[:2]
                self.ext_hygro, self.ext_temp = ext_values[:2]
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


    def reset_global_times(self):
        self.fan_global_time = 0
        self.heater_global_time = 0
        self.dehum_global_time = 0


    def calc_extremum(self):
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

    def update_fan_stats(self):
        self.fan_global_time += self.app.fan.cycle_uptime/3600
        self.fan_energy = round(self.fan_global_time *
            configuration.fan_power/1e3, 1)
        self.app.fan.cycle_uptime = 0

    def update_heater_stats(self):
        self.heater_global_time += self.heater_uptime/3600
        self.heater_energy = round(self.heater_global_time *
            configuration.heater_power/1e3, 1)
        self.heater_uptime = 0

    def update_dehum_stats(self):
        self.dehum_global_time += self.dehum_uptime/3600
        self.dehum_energy = round(self.dehum_global_time *
            configuration.dehum_power/1e3, 1)
        self.dehum_uptime = 0

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            if self.update_values():
                self.calc_extremum()
                self.update_fan_stats()
                self.update_heater_stats()
                self.update_dehum_stats()
            if (monotonic.time.time() - self.log_time) > 10:
                self.save_to_file()
                self.log_time = monotonic.time.time()
            time.sleep(1)
        print "[-] Stopping stats module"
