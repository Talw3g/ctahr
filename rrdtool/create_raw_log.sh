#!/usr/bin/env bash

rrdtool create raw.rrd \
  --start now --step 1  \
  DS:int_temp:GAUGE:300:U:U \
  DS:ext_temp:GAUGE:300:U:U \
  DS:int_hygro:GAUGE:300:U:U \
  DS:ext_hygro:GAUGE:300:U:U \
  RRA:AVERAGE:0.5:1:172800  \
