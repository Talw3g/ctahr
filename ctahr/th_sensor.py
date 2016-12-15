import threading

import Adafruit_DHT as DHT

class CtahrThermoHygroSensor(threading.Thread):
    daemon = True

    def __init__(self, pin):
        threading.Thread.__init__(self)
        self.pin = pin

        self.lock = threading.Lock()

        self.values = None

    def get(self):
        """ Return a (hygro, temperature) tuple in floats (% hum, deg C),
            None if not ready"""
        with self.lock:
            vs = self.values
        return vs

    def run(self):
        while True:
            vs = DHT.read_retry(DHT.DHT22, self.pin)
            with self.lock:
                self.values = vs
