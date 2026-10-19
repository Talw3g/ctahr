
import time,csv,os
from multiprocessing import Process,Array,Event
import Adafruit_DHT as DHT
from .dev_filter import StdDevFilter

class CtahrThermoHygroSensor:
    daemon = True

    def __init__(self, pin, name):
        self.pin = pin
        self.name = name

        self.process = None
        self.quit_event = Event()
        self.values_wrapper = Array('d', [0, 0, time.monotonic(), 0])

    def get(self):
        """ Return a (hygro, temperature) tuple in floats (% hum, deg C),
            None if not ready"""
        return self.values_wrapper[:]

    def start(self):
        self.process = Process(target=self.run,
            args=(self.values_wrapper,self.pin, self.name, self.quit_event))
        self.process.start()

    def stop(self):
        self.quit_event.set()

    @staticmethod
    def run(values_wrapper, pin, name, quit_event):
        print("[+] Starting", name, "sensors module")

        temp_filter = StdDevFilter(3,50)
        hygro_filter = StdDevFilter(3,50)
        while not quit_event.is_set():
            hygro,temp = DHT.read_retry(DHT.DHT22, pin)
            if hygro != None and temp != None:
                hygro, valid_H = hygro_filter.do(hygro,'H')
                temp, valid_T = temp_filter.do(temp,'T')

                if valid_H and valid_T:
                    valid = 1
                else:
                    valid = 0
                values_wrapper[:] = round(hygro,1), round(temp,1), time.monotonic(), valid

            else:
                values_wrapper[3] = 0

            quit_event.wait(timeout = 3)

        print("[-] Stopping", name, "sensors module")

