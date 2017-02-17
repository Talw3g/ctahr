
import os,sys,time
import threading
import RPi.GPIO as GPIO
from serial import Serial
from . import configuration
from .display_lib import DisplayLib

class CtahrDisplay(threading.Thread):
    daemon = True

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.running = True
        # Configuring light sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(configuration.light_sensor_pin, GPIO.IN)

        # Initializing variables
        self.lib = DisplayLib()
        self.app = app
        self.state = 'CURRENT'
        self.states_list = ['CURRENT','TEMP','POWER']
        self.states_indice = 0
        self.t_state = 0
        self.reset_toggle = False

        self.int_hygro = None
        self.int_temp = None
        self.ext_temp = None
        self.ext_hygro = None

    def update_values(self):
        """ Get latest values of Temp and Hygro """
        int_values = self.app.thermohygro_interior.get()
        ext_values = self.app.thermohygro_exterior.get()
        if int_values[3] != 0:
            self.int_hygro, self.int_temp, *rest = int_values
        if ext_values[3] != 0:
            self.ext_hygro, self.ext_temp, *rest = ext_values

    def light_state(self):
        if GPIO.input(configuration.light_sensor_pin) == 1:
            self.lib.backlight(False)
            self.lib.clear()
        else:
            self.lib.backlight(True)

    def cycle_states(self):
        self.states_indice = ((self.states_indice + 1) % len(self.states_list))
        self.state = self.states_list[self.states_indice]
        self.lib.clear()
        self.t_state = 0

    def update_state(self):
        if self.state == 'CURRENT':
            self.update_values()
            self.lib.home()
            self.lib.write('INT:')
            self.lib.write(self.lib.goto(3,1))
            self.lib.write('EXT:')
            self.lib.write(self.lib.goto(1,9))
            self.lib.write(b'\x01')
            self.lib.write(self.lib.goto(3,9))
            self.lib.write(b'\x01')
            self.lib.write(self.lib.goto(2,9))
            self.lib.write(b'\x00')
            self.lib.write(self.lib.goto(4,9))
            self.lib.write(b'\x00')
            self.lib.justify_R(1,16,self.int_temp,'T')
            self.lib.justify_R(2,16,self.int_hygro,'H')
            self.lib.justify_R(3,16,self.ext_temp,'T')
            self.lib.justify_R(4,16,self.ext_hygro,'H')

        elif self.state == 'TEMP':
            self.lib.home()
            self.lib.write('Int max:')
            self.lib.write(self.lib.goto(2,5))
            self.lib.write('min:')
            self.lib.write(self.lib.goto(3,1))
            self.lib.write('Ext max:')
            self.lib.write(self.lib.goto(4,5))
            self.lib.write('min:')
            self.lib.justify_R(1,16,self.app.stats.int_temp_max, 'T')
            self.lib.justify_R(2,16,self.app.stats.int_temp_min, 'T')
            self.lib.justify_R(3,16,self.app.stats.ext_temp_max, 'T')
            self.lib.justify_R(4,16,self.app.stats.ext_temp_min, 'T')

        elif self.state == 'POWER':
            self.lib.center(1,'ENERGY CONSUMPTION')
            self.lib.write(self.lib.goto(2,1))
            self.lib.write('Fan:')
            self.lib.write(self.lib.goto(3,1))
            self.lib.write('Heater:')
            self.lib.write(self.lib.goto(4,1))
            self.lib.write('Dehum:')
            self.lib.justify_R(2,20,self.app.stats.fan_energy, 'E')
            self.lib.justify_R(3,20,self.app.stats.heater_energy, 'E')
            self.lib.justify_R(4,20,self.app.stats.dehum_energy, 'E')

        elif self.state == 'RESET':
            self.lib.clear()
            if not self.reset_toggle:
                self.lib.center(2,'RESET')
            self.reset_toggle = not self.reset_toggle


    def stop(self):
        self.running = False

    def run(self):
        print("[+] Starting display manager")

        while self.running:
            self.light_state()
            if (time.monotonic() - self.t_state) > 0.5:
                self.update_state()
                self.t_state = time.monotonic()
            time.sleep(0.1)

        self.lib.clear()
        print("[-] Stopping display manager")
