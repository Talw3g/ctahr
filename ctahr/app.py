
import os,sys,time
import signal
import threading
from utils import ctxt,GREEN
import configuration
import RPi.GPIO as GPIO
from display import CtahrDisplay
from th_sensor import CtahrThermoHygroSensor
from relay import CtahrRelay
from logic import CtahrLogic
from security import CtahrSecurity
from stats import CtahrStats
from buttons import CtahrButtons
from fan import CtahrFan

class CtahrApplication:

    def __init__(self):
        self.not_running = threading.Event()

        print "[+] Starting Ctahr"

        # gracefull shutdown signal handler
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

        # Starting interior sensor daemon
        self.thermohygro_interior = CtahrThermoHygroSensor(
            configuration.thermohygro_sensor_interior_pin, 'interior')
        self.thermohygro_interior.start()

        # Starting exterior sensor daemon
        self.thermohygro_exterior = CtahrThermoHygroSensor(
            configuration.thermohygro_sensor_exterior_pin, 'exterior')
        self.thermohygro_exterior.start()

        # Creating controlled output objects
        self.heater = CtahrRelay(configuration.heater_relay_pin)
        self.dehum = CtahrRelay(configuration.dehum_relay_pin)
        self.led_run = CtahrRelay(configuration.led_run_pin)

        # Starting regulation daemon
        self.logic = CtahrLogic(self)
        self.logic.start()

        # Starting fan manager
        self.fan = CtahrFan(self)
        self.fan.start()

        # Starting buttons manager
        self.buttons = CtahrButtons(self)
        self.buttons.start()

        # Starting display manager
        self.display = CtahrDisplay(self)
        self.display.start()

        # Starting security daemon
        self.security = CtahrSecurity(self)
        self.security.start()

        # Starting stats daemon
        self.stats = CtahrStats(self)
        self.stats.start()

        self.led_run_status = False


    def shutdown(self, signum, frame):
        # perform a gracefull shutdown here ;)

        print "[-] SIGNAL",signum,"received, shutting down gracefully"
        #
        self.not_running.set()

    def run(self):
        while not self.not_running.is_set():
            self.not_running.wait(1)
            self.led_run.activate(self.led_run_status)
            self.led_run_status = not self.led_run_status

        self.stats.stop()
        self.stats.join()
        self.security.stop()
        self.security.join()
        self.fan.stop()
        self.fan.join()
        self.display.stop()
        self.display.join()
        self.buttons.stop()
        self.buttons.join()
        self.logic.stop()
        self.logic.join()
        self.thermohygro_exterior.stop()
        self.thermohygro_interior.stop()

        self.led_run.activate(False)
        GPIO.cleanup()
        print "[-] Ctahr as stopped"
