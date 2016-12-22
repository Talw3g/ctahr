#!/usr/bin/env python

import RPi.GPIO as GPIO
import ctahr.configuration as config

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(config.watchdog_pin, GPIO.OUT, initial=GPIO.LOW)
