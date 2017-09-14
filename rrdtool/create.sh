#!/usr/bin/env bash

rrdtool create ctahr.rrd \
  --start now --step 1  \
  DS:int_temp:GAUGE:300:U:U \
  DS:ext_temp:GAUGE:300:U:U \
  DS:int_hygro:GAUGE:300:U:U \
  DS:ext_hygro:GAUGE:300:U:U \
  DS:fan:GAUGE:300:U:U \
  DS:heater:GAUGE:300:U:U \
  DS:dehum:GAUGE:300:U:U \
  DS:fan_energy:GAUGE:300:U:U \
  DS:heater_energy:GAUGE:300:U:U \
  DS:dehum_energy:GAUGE:300:U:U \
  RRA:AVERAGE:0.5:1:86400  \
  RRA:AVERAGE:0.5:60:43200 \
  RRA:AVERAGE:0.5:3600:8760  \
  RRA:AVERAGE:0.5:28800:21900
