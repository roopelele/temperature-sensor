#!/usr/bin/python

import time
import os
import sys
import RPi.GPIO as GPIO

FOLDER = "/home/pi/temperature"
TIMEZONE = 3
PIN=14
GPIO.setmode(GPIO.BCM)


def read_sensors():
  rtn = {}
  w1_devices = []
  w1_devices = os.listdir("/sys/bus/w1/devices/")
  for deviceid in w1_devices:
    rtn[deviceid] = {}
    rtn[deviceid]['temp_c'] = None
    device_data_file = "/sys/bus/w1/devices/" + deviceid + "/w1_slave"
    if os.path.isfile(device_data_file):
      try:
         f = open(device_data_file, "r")
         data = f.read()
         f.close()
         if "YES" in data:
           (discard, sep, reading) = data.partition(' t=')
           return str(float(reading) / float(1000.0))
         else:
           continue
      except:
        continue
  return "NaN"

def main():
  int_t = int(time.time() + (3600 * TIMEZONE))
  t = time.gmtime(int_t)
  d = time.strftime("%Y-%m-%d", t)
  data = read_sensors()
  minute = str(t.tm_min)
  if len(minute) < 2:
    minute = "0" + minute
  with open(FOLDER + "/logs/" + d, 'a') as file:
    file.write(str(t.tm_hour) + ":" + minute + "=" + data + "\n")
  with open(FOLDER + "/logs/CURRENT", 'w') as file:
    file.write(str(t.tm_hour) + ":" + minute + "=" + data + "\n")

main()
