
import time,csv,os
import monotonic
from multiprocessing import Process,Array
import Adafruit_DHT as DHT
from dev_filter import StdDevFilter

class CtahrThermoHygroSensor:
    daemon = True

    def __init__(self, pin, name):
        self.pin = pin
        self.name = name
        print "[+] Starting " + self.name + " sensors module"

        self.process = None
        self.values_wrapper = Array('d', [0, 0, monotonic.time.time(), 0])

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
        vs_filter = StdDevFilter(3,20)
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
                hygro, valid_H = vs_filter.do(hygro,'H')
                temp, valid_T = vs_filter.do(temp,'T')

                if valid_H and valid_T:
                    valid = 1
                else:
                    valid = 0
                values_wrapper[:] = round(hygro,1), round(temp,1), monotonic.time.time(), valid

            else:
                values_wrapper[3] = 0

            time.sleep(3)

