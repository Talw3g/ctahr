#!/usr/bin/env python3

import os,sys,time,unittest
from ctahr.app import CtahrApplication
from ctahr.mailing import CtahrMailing

class TestCthar(unittest.TestCase):
    def test_mailing(self):
        mail = CtahrMailing()
        mail.connect()
        mail.send_mail("Test Subject","Test Message Body")


if __name__ == '__main__':
    app = CtahrApplication()
    app.run()
