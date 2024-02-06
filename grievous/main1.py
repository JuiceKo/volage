#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

from network import WLAN
from mqtt import MQTTClient
import machine
import time
import machine
import math
import network
import os
import time
import utime
import gc
import pycom
from machine import RTC
from machine import SD
from L76GNSS import L76GNSS
from pycoproc_2 import Pycoproc

pycom.heartbeat(False)
pycom.rgbled(0x0A0A08) # white

time.sleep(2)
gc.enable()

# setup rtc
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')

py = Pycoproc()
if py.read_product_id() != Pycoproc.USB_PID_PYTRACK:
    raise Exception('Not a Pytrack')

time.sleep(1)
l76 = L76GNSS(py, timeout=30, buffer=512)

pybytes_enabled = False
if 'pybytes' in globals():
    if(pybytes.isconnected()):
        print('Pybytes is connected, sending signals to Pybytes')
        pybytes_enabled = True

# sd = SD()
# os.mount(sd, '/sd')
# f = open('/sd/gps-record.txt', 'w')

def settimeout(duration):
    pass

wlan = WLAN(mode=WLAN.STA)
wlan.antenna(WLAN.EXT_ANT)
wlan.connect("Moi", auth=(WLAN.WPA2, "moi123456789"), timeout=5000)

while not wlan.isconnected():
     machine.idle()

print("Connected to Wifi\n")
client = MQTTClient("nogrigbakauwugrievousbakamariagecrottedenez", "broker.hivemq.com", port=1883)
client.settimeout = settimeout
client.connect()

while True:
    coord = l76.coordinates()
    msg="{} - {} - {}".format(coord, rtc.now(), gc.mem_free())
    client.publish("daikan/geoloc", "{}".format(coord))
    print("Push oK")
    time.sleep(10)
    if(pybytes_enabled):
        pybytes.send_signal(1, coord)
        time.sleep(10)
