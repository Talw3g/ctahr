#!/usr/bin/env bash

rrdtool graph temp.png \
  --start -2d -a PNG -w 1500 -h 700 -A -E -y 1:2 \
  -n UNIT:20 -n AXIS:20 -n LEGEND:20 -n WATERMARK:1 -n TITLE:30 \
  --x-grid HOUR:1:DAY:1:HOUR:4:0:%H \
  --vertical-label 'Temperature (°C)' --title 'Temperature'\
  --color=CANVAS#505050 --color=BACK#FFFFFF\
  --border 0 \
  DEF:raw_int=ctahr.rrd:int_temp:AVERAGE \
  CDEF:temp_int=raw_int,UN,0,raw_int,IF \
  DEF:raw_ext=ctahr.rrd:ext_temp:AVERAGE \
  CDEF:temp_ext=raw_ext,UN,0,raw_ext,IF \
  LINE3:temp_int#FF0000:'Interior' \
  LINE3:temp_ext#0000FF:'Exterior'

rrdtool graph temp24h.png \
  --start -24h -a PNG -w 1500 -h 700 -A -E -y 1:2 \
  -n UNIT:20 -n AXIS:20 -n LEGEND:20 -n WATERMARK:1 -n TITLE:30 \
  --x-grid MINUTE:30:HOUR:1:HOUR:1:0:%H \
  --vertical-label 'Temperature (°C)' --title 'Temperature'\
  --color=CANVAS#505050 --color=BACK#FFFFFF\
  --border 0 \
  DEF:raw_int=ctahr.rrd:int_temp:AVERAGE \
  CDEF:temp_int=raw_int,UN,0,raw_int,IF \
  DEF:raw_ext=ctahr.rrd:ext_temp:AVERAGE \
  CDEF:temp_ext=raw_ext,UN,0,raw_ext,IF \
  LINE3:temp_int#FF0000:'Interior' \
  LINE3:temp_ext#0000FF:'Exterior'
#  CDEF:over=temp,10,GT,temp,10,-,0,IF \
#  CDEF:under=temp,10,LT,temp,10,-,0,IF \
#  CDEF:bot=temp,10,GT,10,temp,IF \
#  AREA:temp#97bb66 \
#  LINE5:10#660000  \
#  AREA:over#fb795199:STACK \
#  AREA:under#b3e6ff99:STACK \
#  'LINE2:temp#FF0000:Temperature'

rrdtool graph hygro24h.png \
  --start -24h -a PNG -w 1500 -h 700 -A -E -y 1:2 \
  -n UNIT:20 -n AXIS:20 -n LEGEND:20 -n WATERMARK:1 -n TITLE:30 \
  --x-grid MINUTE:30:HOUR:1:HOUR:1:0:%H \
  --vertical-label 'hygrometry (°C)' --title 'hygrometry'\
  --color=CANVAS#505050 --color=BACK#FFFFFF\
  --border 0 \
  DEF:raw_int=ctahr.rrd:int_hygro:AVERAGE \
  CDEF:hygro_int=raw_int,UN,0,raw_int,IF \
  DEF:raw_ext=ctahr.rrd:ext_hygro:AVERAGE \
  CDEF:hygro_ext=raw_ext,UN,0,raw_ext,IF \
  LINE3:hygro_int#FF0000:'Interior' \
  LINE3:hygro_ext#0000FF:'Exterior'

rrdtool graph energy.png \
  --start -1w -a PNG -w 1500 -h 700 -A -E -y 1:5 \
  -n UNIT:20 -n AXIS:20 -n LEGEND:20 -n WATERMARK:1 -n TITLE:30 \
  --x-grid HOUR:6:DAY:1:DAY:1:86400:%d \
  --vertical-label 'Energy (KWh)' --title 'Energy consumption'\
  --color=CANVAS#505050 --color=BACK#FFFFFF\
  --border 0 \
  DEF:fan_en=ctahr.rrd:fan_energy:AVERAGE \
  DEF:heater_en=ctahr.rrd:heater_energy:AVERAGE \
  DEF:dehum_en=ctahr.rrd:dehum_energy:AVERAGE \
  LINE3:fan_en#FF0000:'Fan' \
  LINE3:heater_en#0000FF:'Heater' \
  LINE3:dehum_en#009933:'Dehumidifier'


rrdtool graph raw_temp24h.png \
  --start -24h -a PNG -w 1500 -h 700 -A -E -y 1:2 \
  -n UNIT:20 -n AXIS:20 -n LEGEND:20 -n WATERMARK:1 -n TITLE:30 \
  --x-grid MINUTE:30:HOUR:1:HOUR:1:0:%H \
  --vertical-label 'Temperature (°C)' --title 'Temperature'\
  --color=CANVAS#505050 --color=BACK#FFFFFF\
  --border 0 \
  DEF:raw_int=int_raw.rrd:int_temp:AVERAGE \
  DEF:raw_ext=ext_raw.rrd:ext_temp:AVERAGE \
  LINE3:raw_int#FF0000:'Interior' \
  LINE3:raw_ext#0000FF:'Exterior'

rrdtool graph raw_hygro24h.png \
  --start -24h -a PNG -w 1500 -h 700 -A -E -y 1:2 \
  -n UNIT:20 -n AXIS:20 -n LEGEND:20 -n WATERMARK:1 -n TITLE:30 \
  --x-grid MINUTE:30:HOUR:1:HOUR:1:0:%H \
  --vertical-label 'Hygro' --title 'Hygro'\
  --color=CANVAS#505050 --color=BACK#FFFFFF\
  --border 0 \
  DEF:raw_int=int_raw.rrd:int_hygro:AVERAGE \
  DEF:raw_ext=ext_raw.rrd:ext_hygro:AVERAGE \
  LINE3:raw_int#FF0000:'Interior' \
  LINE3:raw_ext#0000FF:'Exterior'
