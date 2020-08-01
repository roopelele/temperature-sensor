from flask import Flask, send_file
import time

FOLDER = "/home/pi/temperature"
TIMEZONE = 3

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

def GetCurrentData():
    with open(FOLDER + "/logs/CURRENT", 'r') as file:
        return file.read().split('=')

def GetDate(hour_offset=0):
    int_t = int(time.time() + (3600 * (TIMEZONE + hour_offset)))
    t = time.gmtime(int_t)
    return time.strftime("%Y-%m-%d", t)

@app.route('/')
def hello_world():
    clock, temp = GetCurrentData()
    text  = "<!DOCTYPE html>\n"
    text += "<title>Temperature readings</title>\n"
    text += "<body style=\"background-color:#404040;\">\n"
    text += "  <div>\n"
    text += "    <p style=\"color:#aaaaaa;\">Current time: {}</p>\n".format(clock)
    text += "    <p style=\"color:#aaaaaa;\">Current temperature: {}</p>\n".format(temp)
    text += "    <img src=\"http://192.168.100.12:5000/graph/\">\n"
    text += "  </div>\n"
    text += "</body>\n"
    return text

@app.route('/graph/')
def get_image():
    return send_file(FOLDER + "/graphs/" + GetDate(-1) + ".png", mimetype='image/gif')
