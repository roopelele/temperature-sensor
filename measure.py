#!/usr/bin/python

import time
import os
import sys
import json
import RPi.GPIO as GPIO

FOLDER = "/home/pi/temperature"
TIMEZONE = 3
PIN = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)



def read_sensors():
    rtn = {}
    w1_devices = []
    w1_devices = os.listdir("/sys/bus/w1/devices/")
    values = []
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
                    values.append(float(reading) / 1000.0)
                else:
                    continue
            except:
                continue
    if len(values) != 0:
        return {'success': True, 'values': values}
    else:
        return {'success': False}


def main():
    int_t = int(time.time() + (3600 * TIMEZONE))
    t = time.gmtime(int_t)
    d = time.strftime("%Y-%m-%d", t)
    data = read_sensors()
    if not data['success']:
        return
    minute = str(t.tm_min)
    if len(minute) < 2:
        minute = "0" + minute
    for i, value in enumerate(data['values']):
        with open(f"{FOLDER}/logs/{d}_{i}", 'a') as outfile:
            outfile.write(f"{str(t.tm_hour)}:{minute}={value}\n")
    data['clock'] = f"{str(t.tm_hour)}:{minute}"
    with open(FOLDER + "/logs/CURRENT.json", 'w') as outfile:
        json.dump(data, outfile)


main()
