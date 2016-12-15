
import time
import threading

class CtahrLogic(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app

    def run(self):
        while True:
            vs = self.app.thermohygro_interior.get()

            time.sleep(1)
