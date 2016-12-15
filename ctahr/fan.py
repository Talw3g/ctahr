
import threading,time

def CtahrFan(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.lock = threading.Lock()
        self.state = 'IDLE'

        self.starting_time_s = None

    def turn_on(self):
        with self.lock:
            self.state = 'STARTING'

    def turn_off(self):
        with self.lock:
            self.state = 'STOPPING'

    def run(self):
        while True:
            with self.lock:
                self.update_state_machine()
                time.sleep(0.1)

    def update_state_machine(self):
        if self.state == 'IDLE':
            # nothing to do
            pass

        elif self.state == 'STARTING':
            #servo.set(100)
            #relay.set(1)

            self.starting_time_s = time.time()
            self.state = 'STARTING_WAIT'

        elif self.state == 'STARTING_WAIT':
            if time.time() - self.starting_time_s > 1.0:
                self.state = 'RUNNING'

        elif self.state == 'RUNNING':
            pass

        elif self.state == 'STOPPING':
            pass

