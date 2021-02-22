from flask import Flask, send_file, request, redirect, json, make_response
from flask_cors import CORS
import time
import json
import sys
import os

app = Flask(__name__)
CORS(app, origins='*')
app.config['CORS_HEADERS'] = 'Content-Type'

UPDATEIP = "192.168.1.39"
FOLDER = "/home/pi/temperature"
TIMEZONE = 2
DEBUG_MODE = False
data = {'success': False, 'values': [], 'clock': ""}
history = []
lastReload = 0

def load_config():
    print("Loading config...", file=sys.stderr)
    with open(f"{FOLDER}/config.json", 'r') as infile:
        return json.load(infile)

def load_current():
    with open(os.path.join(FOLDER, 'logs', 'current.json'), 'r') as infile:
        return json.load(infile)

def load_old():
    newHistory = []
    int_t = int(time.time() + (3600 * TIMEZONE))
    t = time.gmtime(int_t)
    d = time.strftime("%Y-%m-%d", t)
    for infile in os.listdir(f"{FOLDER}/logs"):
        if d in infile:
            tmp = []
            try:
                with open(f"{FOLDER}/logs/{infile}", 'r') as datafile:
                    tmp = datafile.readlines()
            except IOError:
                print("IOError")
                continue
            deviceid = infile.split('_')[-1]
            newHistory.append({"name": deviceid, "temps": [], "times": []})
            for entry in tmp:
                s = entry.rstrip("\n").split('=')
                newHistory[-1]["times"].append(s[0])
                newHistory[-1]["temps"].append(s[1])
    return newHistory

@app.route('/', methods=["GET"])
def main():
    return app.response_class(
        response="",
        status=200,
        content_type='text/plain',
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"},
    )

@app.route('/current/', methods=['GET'])
def get_current_data():
    global data
    data = load_current()
    d = {'config': config, 'data': data}
    return app.response_class(
        response=json.dumps(d),
        status=200,
        content_type='application/json',
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"},
    )

@app.route('/history/', methods=["GET"])
def get_history():
    global lastReload, history
    if int(time.time()) - lastReload > 60:
        lastReload = int(time.time())
        tmp = load_old()
        if tmp != []:
            history = tmp
        else:
            print("error, using old history data")
    d = {'config': config, 'data': history}
    return app.response_class(
        response=json.dumps(d),
        status=200,
        content_type='application/json',
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"},
    )

@app.route('/config/', methods=["GET"])
def get_config():
    return app.response_class(
        response=json.dumps(config),
        status=200,
        content_type='application/json',
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"},
    )

config = load_config()

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE, host='0.0.0.0')
