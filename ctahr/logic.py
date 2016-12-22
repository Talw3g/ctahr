
import threading,time
import configuration

class CtahrLogic(threading.Thread):
    daemon = True
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.app = app
        self.temp_state = 'CHECK'
        self.hygro_state = 'CHECK'
        self.fan_vote = [False,False]
        self.fan = False
        self.heat = False
        self.dehum = False
        self.temp_targ_err = 0
        self.temp_ext_err = 0
        self.hygro_err = 0
        self.running = True
        self.block_dehum = False
        self.daily_uptime = 0
        self.int_temp = 0
        self.ext_temp = 0
        self.aired_time = time.time()


    def update_temp(self):
        if self.temp_state == 'CHECK':
            self.fan_vote[0] = False
            self.heat = False
            self.block_dehum = False
            if self.temp_targ_err < -configuration.delta_targ_H:
                self.temp_state = 'CHILL'
            elif self.temp_targ_err > configuration.delta_targ_H:
                self.temp_state = 'WARM'

        elif self.temp_state == 'CHILL':
            if self.temp_ext_err < -configuration.delta_ext_H:
                self.temp_state = 'VENTILATE'
                self.block_dehum = True
            else:
                self.temp_state = 'CHECK'

        elif self.temp_state == 'WARM':
            if self.temp_targ_err > configuration.delta_freeze_H:
                self.temp_state = 'HEAT'
            elif self.temp_ext_err > configuration.delta_ext_H:
                self.temp_state = 'VENTILATE'
            else:
                self.temp_state = 'CHECK'

        elif self.temp_state == 'VENTILATE':
            if (abs(self.temp_targ_err) < configuration.delta_targ_L or
                abs(self.temp_ext_err) < configuration.delta_ext_L):
                self.temp_state = 'CHECK'
            elif self.temp_targ_err > configuration.delta_freeze_H:
                self.temp_state = 'HEAT'
                self.fan_vote[0] = False
            else:
                self.fan_vote[0] = True

        elif self.temp_state == 'HEAT':
            if self.temp_targ_err < configuration.delta_freeze_L:
                self.temp_state = 'CHECK'
            else:
                self.heat = True


    def update_hygro(self):
        if self.hygro_state == 'CHECK':
            if (self.hygro_err < -configuration.delta_hygro and
                    not self.block_dehum):
                self.hygro_state = 'DEHUM'
            else:
                self.dehum = False

        elif self.hygro_state == 'DEHUM':
            if (self.hygro_err > 0 or self.block_dehum):
                self.hygro_state = 'CHECK'
            else:
                self.dehum = True


    def update_values(self):
        int_values = self.app.thermohygro_interior.get()
        ext_values = self.app.thermohygro_exterior.get()
        int_valid, ext_valid = int_values[3], ext_values[3]
        if int_valid != 0 and ext_valid != 0:
            with self.lock:
                self.int_hygro, self.int_temp = int_values[:2]
                self.ext_hygro, self.ext_temp = ext_values[:2]
            return True
        else:
            return False

    def calc_err_targ(self):
        self.temp_targ_err = configuration.temp_target - self.int_temp
        self.temp_ext_err = self.ext_temp - self.int_temp
        self.airing_err = abs(configuration.temp_target - self.ext_temp)
        if self.temp_targ_err < -configuration.delta_targ_H:
            self.hygro_target = configuration.hygro_target_summer
        else:
            self.hygro_target = configuration.hygro_target_winter
        self.hygro_err = self.hygro_target - self.int_hygro


    def daily_airing(self):
        temp_optimal = self.airing_err < configuration.delta_targ_H
        unaired = (time.time() - self.aired_time) > configuration.daily_period
        damp = self.ext_hygro > self.hygro_target
        self.daily_uptime = self.app.fan.get_uptime()

        if self.daily_uptime > configuration.daily_airing_time:
            self.app.fan.reset_uptime()
            self.aired_time = time.time()
            self.fan_vote[1] = False
        elif temp_optimal and unaired and not damp:
            self.fan_vote[1] = True
        else:
            self.fan_vote[1] = False


    def decide_ventilate(self):
        temp_control, daily_airing = self.fan_vote
        self.fan = temp_control or (daily_airing and not self.dehum)


    def stop(self):
        self.running = False
        self.fan = False
        self.heat = False
        self.dehum = False

    def run(self):
        while self.running:
            if self.update_values():
                self.calc_err_targ()
                self.daily_airing()
            self.update_temp()
            self.update_hygro()
            self.decide_ventilate()
            time.sleep(1)
        print "[-] Stopping logic module"
