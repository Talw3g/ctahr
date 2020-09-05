
import os
from rrdtool import update
from .mailing import CtahrMailing
from datetime import datetime
from . import configuration

class CtahrLogging():

    def __init__(self, app):
        self.app = app
        self.mail = CtahrMailing()
        self.err_count = 0
        self.err_content = ""

    def log(self):
        try:
            update(configuration.rrdtool_file,"N:%f:%f:%f:%f:%d:%d:%d:%f:%f:%f"
                %(self.app.logic.int_temp, self.app.logic.ext_temp,
                self.app.logic.int_hygro, self.app.logic.ext_hygro,
                int(self.app.logic.fan), int(self.app.logic.heat),
                int(self.app.logic.dehum), self.app.stats.fan_energy,
                self.app.stats.heater_energy, self.app.stats.dehum_energy))
            self.err_count = 0
            self.err_content = ""
        except Exception as e:
            self.err_count += 1
            self.err_content += "\n*******\n"
            self.err_content += str(e)
            if self.err_count > 10:
                self.warn()

    def warn(self):
        subject = 'RRD logging is not working'

        message = datetime.now().strftime("%Y-%m-%d %H:%M:%S : \n")
        message += self.err_content
        if self.mail.connect():
            self.mail.send_mail(subject, message)
            self.err_count = 0
            self.err_content = ""
