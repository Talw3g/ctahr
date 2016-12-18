import os,sys,time
import threading
from Queue import Queue
import RPi.GPIO as GPIO
import configuration
from serial import Serial

class CtahrDisplay(threading.Thread):
    daemon = True

    def __init__(self):
        threading.Thread.__init__(self)

        print "[+] Starting display manager"

        self.serial = Serial(
            configuration.display_serial_device,
            configuration.display_serial_speed)

        self.serial.write('\xfe\x52')
        self.clear()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(configuration.light_sensor_pin, GPIO.IN)

        self.int_hygro = None
        self.int_temp = None
        self.ext_temp = None
        self.ext_hygro = None

    def update_values(self, int_values, ext_values):
        """ Get latest values of Temp and Hygro """
        if int_values != None:
            self.int_hygro, self.int_temp, self.int_time = int_values
        if ext_values != None:
            self.ext_hygro, self.ext_temp, self.ext_time = ext_values

    def clear(self):
        """ Clear display """
        self.serial.write('\xfe\x58')

    def light_state(self):
        if GPIO.input(configuration.light_sensor_pin) == 1:
            self.serial.write('\xfe\x46')
            self.clear()
        else:
            self.serial.write('\xfe\x42\0')

    def run(self):
        while True:
#            self.clear()
            self.light_state()
            msg = ('Interior Temp:' + str(self.int_temp) + '\xb2C\n'
                + 'Exterior Temp:' + str(self.ext_temp) + '\xb2C\n'
                + 'Interior Hygro:' + str(self.int_hygro) + '\x25\n'
                + 'Exterior Hygro:' + str(self.ext_hygro)+ '\x25')
            self.serial.write('\xfe\x48')
            self.serial.write(msg)
            time.sleep(1)
