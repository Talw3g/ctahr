
import threading,time
import csv

class CtahrStats(threading.Thread):
    daemon = True

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.lock = threading.Lock()


    def update_values(self):
        int_values = self.app.thermohygro_interior.get()
        ext_values = self.app.thermohygro_exterior.get()
        if int_values != None:
            with self.lock:
                self.int_hygro, self.int_temp, int_time = int_values
        if ext_values != None:
            with self.lock:
                self.ext_hygro, self.ext_temp, ext_time = ext_values


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
