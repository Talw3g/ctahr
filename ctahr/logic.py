
import threading,time
import configuration

class CtahrLogic(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.state = 'INIT'
        self.summer = False

    def update(self):
        if self.state == 'INIT':
            self.state = 'CHECK'

        elif self.state == 'CHECK':
            if self.int_temp < configuration.temp_low:
                self.state = 'COOL'
            elif self.int_temp > configuration.temp_high:
                self.state = 'WARM'
            elif self.int_hygro > self.hygro_high:
                self.state = 'DRY'

    def run(self):
        while True:
            self.int_hygro,self.int_temp,self.int_ts = self.app.thermohygro_interior.get()
            self.ext_hygro,self.ext_temp,self.ext_ts = self.app.thermohygro_exterior.get()
            if self.ext_temp > configuration.summer_temp:
                self.hygro_low = configuration.summer_hygro_low
                self.hygro_high = configuration.summer_hygro_high
            else:
                self.hygro_low = configuration.winter_hygro_low
                self.hygro_high = configuration.winter_hygro_high

            self.update()

            time.sleep(1)
