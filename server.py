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
canReload = True

def load_config():
    print("Loading config...", file=sys.stderr)
    with open(f"{FOLDER}/config.json", 'r') as infile:
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

@app.route('/get_data/', methods=["POST", "OPTIONS"])
def get_data():
    if request.method == "OPTIONS": # CORS preflight
        return app.response_class(
        response="OK",
        status=200,
        content_type='text/plain',
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"},
    )
    #print(f"\nclient ip: {request.remote_addr}\nreceived form: {request.json}\n")
    data = request.json
    start = data['start']
    end = data['end']
    with open(f"{FOLDER}/logs/data.csv") as datafile:
        lines = datafile.readlines()
    resp = {"temps": [], "times": []}
    for line in lines:
        tmp = line.rstrip("\n").rstrip("_0").split(',')
        if start <= tmp[0] <= end:
            resp["temps"].append(tmp[1])
            resp["times"].append(tmp[0])
    return app.response_class(
        response=json.dumps(resp),
        status=200,
        content_type='application/json',
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"},
    )

@app.route('/update/', methods=['POST'])
def update_data():
    if request.remote_addr != UPDATEIP: # IP not allowed, return 401
        return app.response_class(
            response="client-not-allowed",
            status=401,
            content_type='text/plain'
        )
    else:
        global canReload
        canReload = True
        temp = request.json
        if not temp["success"]:
            print("error in update")
            return app.response_class(
                response="ERROR",
                status=404,
                content_type='text/plain',
                headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"},
            )
        global data
        data = temp
        return app.response_class(
            response="OK",
            status=200,
            content_type='text/plain',
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"},
        )

@app.route('/current/', methods=['GET'])
def get_current_data():
    d = {'config': config, 'data': data}
    return app.response_class(
        response=json.dumps(d),
        status=200,
        content_type='application/json',
        headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"},
    )

@app.route('/history/', methods=["GET"])
def get_history():
    global canReload
    if canReload:
        canReload = False
        global history
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
