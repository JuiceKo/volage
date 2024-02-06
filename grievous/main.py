from network import LoRa
import socket
import binascii
import struct
import time
import config
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
import time
import pycom
import struct
from machine import Pin
import machine
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# create an OTA authentication params
dev_eui = binascii.unhexlify('70B3D5499F6D1E1F')
app_eui = binascii.unhexlify('0000000000000000')
app_key = binascii.unhexlify('1CE2DCD321C1BA1894089B1EB293F824')

# set the 3 default channels to the same frequency (must be before sending the OTAA join request)
lora.add_channel(0, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
lora.add_channel(1, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
lora.add_channel(2, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)

# join a network using OTAA
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0, dr=config.LORA_NODE_DR)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not joined yet...')

# remove all the non-default channels
for i in range(3, 16):
    lora.remove_channel(i)

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, config.LORA_NODE_DR)

# make the socket non-blocking
s.setblocking(False)

time.sleep(5.0)

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


coord = l76.coordinates()
import struct
msg="{}".format(coord)
print(msg)
def encode_coordinates(lat, lon):
    lat = (lat + 90) / 180 * 16777215
    lon = (lon + 180) / 360 * 16777215

    # Encoder en 3 octets pour chaque coordonnée
    lat_bytes = int(lat).to_bytes(3, 'big')
    lon_bytes = int(lon).to_bytes(3, 'big')
    # Concaténer les bytes de la latitude et de la longitude
    return lat_bytes + lon_bytes

# Exemple d'utilisation
encoded = encode_coordinates(*coord)
print(encoded)

def accelerometer():
print("ACCELEROMETER:", "accel:", accelerometer_sensor.acceleration(), "roll:", accelerometer_sensor.roll(), "pitch:", accelerometer_sensor.pitch(), "x/y/z:", accelerometer_sensor.x, accelerometer_sensor.y, accelerometer_sensor.z )


for i in range (200):
    pkt = encoded
    print('Sending:', pkt)
    s.send(pkt)

    rx, port = s.recvfrom(256)
    if rx:
        print('Received: {}, on port: {}'.format(rx, port))
    time.sleep(200)



    ###############################################################
    print("10 secondes pour téléchargement !")
    time.sleep(10)


    sleep_time_s = 300 # 5 min
    print("pycoproc init")
    py = Pycoproc()
    pycom.heartbeat(False)
    pycom.rgbled(0x7F0000) # red
    time.sleep(2)
    print("battery {:.2f} V".format(py.read_battery_voltage()))
    #py.setup_sleep(sleep_time_s)

    print("setup sleep OK !")
    # init accelerometer
    accelerometer_sensor = LIS2HH12()
    # read accelerometer sensor values
    print("read accelerometer OK !")
    accelerometer()
    print("enable accelerometer interrupt")

    # enable_activity_interrupt( [mG], [ms], callback)
    # accelerometer_sensor.enable_activity_interrupt(8000, 200, activity_int_handler) # low sensitivty
    #accelerometer_sensor.enable_activity_interrupt(2000, 200, activity_int_handler) # medium sensitivity
    accelerometer_sensor.enable_activity_interrupt(2000, 200) # medium sensitivity
    # accelerometer_sensor.enable_activity_interrupt( 100, 200, activity_int_handler) # high sensitivity
    # accelerometer_sensor.enable_activity_interrupt(63, 160, activity_int_handler) # ultra sensitivty

    print("enable pycom module to wake up from accelerometer interrupt")
    wake_pins = [Pin('P13', mode=Pin.IN, pull=Pin.PULL_DOWN)]
    machine.pin_sleep_wakeup(wake_pins, machine.WAKEUP_ANY_HIGH, True)

    print("put pycoproc to sleep and pycom module to deepsleep")
    pycom.rgbled(0xFFFFFF) # white
    time.sleep(1)
    pycom.rgbled(0x000000) # white
    time.sleep(1)
    pycom.rgbled(0xFFFFFF) # white
    time.sleep(1)
    pycom.rgbled(0x000000) # white
    time.sleep(1)
    pycom.rgbled(0xFFFFFF) # white
    time.sleep(1)
    #pycom.rgbled(0x000000) # white
    #time.sleep(1)
    py.go_to_sleep(pycom_module_off=False, accelerometer_off=False, wake_interrupt=True)
    #machine.deepsleep(sleep_time_s * 1000)
    machine.deepsleep()

    print("we never reach here!")
