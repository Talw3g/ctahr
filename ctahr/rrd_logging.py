
import os
import rrdtool as rrd
from . import configuration

class CtahrLogging():

    def __init__(self, app):
        self.app = app

    def log(self):
        rrd.update(configuration.rrdtool_file,"N:%f:%f:%f:%f:%d:%d:%d:%f:%f:%f"
            %(self.app.logic.int_temp, self.app.logic.ext_temp,
            self.app.logic.int_hygro, self.app.logic.ext_hygro,
            int(self.app.logic.fan), int(self.app.logic.heat),
            int(self.app.logic.dehum), self.app.stats.fan_energy,
            self.app.stats.heater_energy, self.app.stats.dehum_energy))

