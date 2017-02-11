
import os
from . import configuration

class CtahrLogging():

    def __init__(self, app):
        self.app = app

    def log(self):
        os.system("rrdtool update %s N:%f:%f:%f:%f:%d:%d:%d:%f:%f:%f"
            %(configuration.rrdtool_file,
            self.app.logic.int_temp, self.app.logic.ext_temp,
            self.app.logic.int_hygro, self.app.logic.ext_hygro,
            int(self.app.logic.fan), int(self.app.logic.heat),
            int(self.app.logic.dehum), self.app.stats.fan_energy,
            self.app.stats.heater_energy, self.app.stats.dehum_energy))

