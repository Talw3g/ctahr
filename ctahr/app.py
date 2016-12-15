
import os,sys,time
import signal
import threading
from utils import ctxt,GREEN
import configuration

from display import CtahrDisplay
from th_sensor import CtahrThermoHygroSensor
from relay import CtahrRelay
from logic import CtahrLogic

class CtahrApplication:

    def __init__(self):
        self.not_running = threading.Event()

        print "[+] Starting Ctahr"

        # gracefull shutdown signal handler
        signal.signal(signal.SIGTERM, self.shutdown)

        #
        self.display = CtahrDisplay()
        self.display.start()

        self.thermohygro_exterior = CtahrThermoHygroSensor(
            configuration.thermohygro_sensor_exterior_pin)
        self.thermohygro_exterior.start()

        self.thermohygro_interior = CtahrThermoHygroSensor(
            configuration.thermohygro_sensor_interior_pin)
        self.thermohygro_interior.start()

        self.heater = CtahrRelay(configuration.heater_relay_pin)
        self.dehum = CtahrRelay(configuration.dehum_relay_pin)

        self.logic = CtahrLogic(self)
        self.logic.start()

    def shutdown(self, signum, frame):
        # perform a gracefull shutdown here ;)

        print "[+] SIGNAL",signum,"received, shutting down gracefully"
        #
        self.not_running.set()

    def run(self):
        while not self.not_running.is_set():

            self.not_running.wait(1)

            vs = self.thermohygro_exterior.get()
            self.display.write(str(vs))

        print "[+] Ctahr as stopped"
