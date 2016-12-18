
import threading,time

def CtahrSecurity(threading.Thread):
   def __init__(self):
       threading.Thread.__init__(self)
       self.lock = threading.Lock()

    def check_freshness(self, int_values, ext_values):
        if (time.time() - int_values[2]) > 300:
            self.alarm('int_outdated',int_values)

        if (time.time() - ext_values[2]) > 300:
            self.alarm('ext_outdated',ext_values)


