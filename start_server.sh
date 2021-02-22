#!/bin/sh
cd /home/pi/temperature
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - server:app
