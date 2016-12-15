import os,sys,time
import threading
from Queue import Queue

import configuration
import serial

class CtahrDisplay(threading.Thread):
    daemon = True

    def __init__(self):
        threading.Thread.__init__(self)

        print "[+] Starting display manager"

        self.serial = serial.Serial(
            configuration.display_serial_device,
            configuration.display_serial_speed)

        self.msg_queue = Queue()

    def write(self, txt):
        """ Write message on display """
        self.msg_queue.put("%s\n"%txt)

    def run(self):
        while True:
            msg = self.msg_queue.get()
            print "[?] DISPLAY:",msg
            self.serial.write(msg)
