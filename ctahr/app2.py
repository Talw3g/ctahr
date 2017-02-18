
import threading, signal
from . import configuration
from .webserver import CtahrWebServer
from .wrapper import JSONWrapper
from .dummy import DummyValues

class CtahrApplication:

    def __init__(self):
        self.not_running = threading.Event()
        print("[+] Starting Ctahr")

        # gracefull shutdown signal handler
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

        # Creating wrapper
        self.wrapper = JSONWrapper(self)

        # Starting web server
        self.webserver = CtahrWebServer(self)
        self.webserver.start()

        self.dummy = DummyValues()

    def shutdown(self, signum, frame):
        print("[-] SIGNAL", signum,
            "received, shutting down gracefully")
        self.not_running.set()

    def run(self):
        while not self.not_running.is_set():
            self.not_running.wait(1)

        self.webserver.stop()
        print("[-] Ctahr has stopped")
