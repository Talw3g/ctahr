import threading,time

import Adafruit_DHT as DHT

class CtahrThermoHygroSensor(threading.Thread):
    daemon = True

    def __init__(self, pin, name):
        threading.Thread.__init__(self)
        self.pin = pin
        self.name = name
        self.running = True
        print "[+] Starting " + self.name + " sensors module"

        self.lock = threading.Lock()

        self.values = None

    def get(self):
        """ Return a (hygro, temperature) tuple in floats (% hum, deg C),
            None if not ready"""
        with self.lock:
            vs = self.values
        return vs

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            hygro,temp = DHT.read_retry(DHT.DHT22, self.pin)
            if hygro != None and temp != None:
                vs = (round(hygro,1),round(temp,1),time.time())
                with self.lock:
                    self.values = vs
            time.sleep(10)
        print "[-] Stopping " + self.name + " sensors module"
