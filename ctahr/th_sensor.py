import time,csv
from multiprocessing import Process,Array

import Adafruit_DHT as DHT

class CtahrThermoHygroSensor:
    daemon = True

    def __init__(self, pin, name):
        self.pin = pin
        self.name = name
        print "[+] Starting " + self.name + " sensors module"

        self.process = None
        self.values_wrapper = Array('d', [0, 0, time.time(), 0])

    def get(self):
        """ Return a (hygro, temperature) tuple in floats (% hum, deg C),
            None if not ready"""
        return self.values_wrapper[:]

    def start(self):
        self.process = Process(target=self.run, args=(self.values_wrapper,self.pin, self.name))
        self.process.start()

    def stop(self):
        if self.process is not None:
            self.process.terminate()

    @staticmethod
    def run(values_wrapper, pin, name):
        while True:
           # if name == 'interior':
           #     f = '/opt/ctahr/ctahr/int.csv'
           # else:
           #     f = '/opt/ctahr/ctahr/ext.csv'
           # for row in csv.reader(open(f,'rb'), delimiter=','):
           #     hygro,temp = row
           #     hygro = float(hygro)
           #     temp = float(temp)
            hygro,temp = DHT.read_retry(DHT.DHT22, pin)
            if hygro != None and temp != None:
                try:
                    var_temp = abs(prev_temp - temp)
                except:
                    var_temp = 0

                if var_temp < 5:
                    values_wrapper[:] = round(hygro,1), round(temp,1), time.time(), 1
                    prev_temp = temp
                else:
                    values_wrapper[3] = 0
            else:
                values_wrapper[3] = 0
            time.sleep(3)

if __name__ == '__main__':
    cth = CtahrThermoHygroSensor(17,"x")
    cth.start()
    time.sleep(1)
    print cth.get()
    time.sleep(1)
    print cth.get()
    time.sleep(1)
    print cth.get()
    cth.stop()
