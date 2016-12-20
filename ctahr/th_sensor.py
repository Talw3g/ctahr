import time
from multiprocessing import Process,Array

import Adafruit_DHT as DHT

class CtahrThermoHygroSensor:
    daemon = True

    def __init__(self, pin, name):
        self.pin = pin
        self.name = name
        print "[+] Starting " + self.name + " sensors module"

        self.process = None
        self.values_wrapper = Array('d', 3)

    def get(self):
        """ Return a (hygro, temperature) tuple in floats (% hum, deg C),
            None if not ready"""
        return self.values_wrapper[:]

    def start(self):
        self.process = Process(target=self.run, args=(self.values_wrapper,self.pin))
        self.process.start()

    def stop(self):
        if self.process is not None:
            self.process.terminate()

    @staticmethod
    def run(values_wrapper, pin):
        while True:
            hygro,temp = DHT.read_retry(DHT.DHT22, pin)
            if hygro != None and temp != None:
                values_wrapper[:] = round(hygro,1),round(temp,1),time.time()
            time.sleep(1)

if __name__ == '__main__':
    cth = CtahrThermoHygroSensor(0,"x")
    cth.start()
    time.sleep(1)
    print cth.get()
    time.sleep(1)
    print cth.get()
    time.sleep(1)
    print cth.get()
    cth.stop()
