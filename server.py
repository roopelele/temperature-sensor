from flask import Flask, send_file, request, redirect, json, make_response
from flask_cors import CORS
import time
import json
import sys
import os

app = Flask(__name__)
CORS(app, origins='*')
app.config['CORS_HEADERS'] = 'Content-Type'

FOLDER = "/home/pi/temperature"
TIMEZONE = 2
DEBUG_MODE = True
data = {'success': False, 'values': [], 'clock': ""}
history = []

def load_config():
    with open(f"{FOLDER}/config.json", 'r') as infile:
        return json.load(infile)


def load_old():
    int_t = int(time.time() + (3600 * TIMEZONE))
    t = time.gmtime(int_t)
    d = time.strftime("%Y-%m-%d", t)
    rtn = {"temps": [], "times": []}
    with open(f"{FOLDER}/logs/{d}_0", 'r') as datafile:
        tmp = datafile.readlines()
    for entry in tmp:
        s = entry.rstrip("\n").split('=')
        rtn["times"].append(s[0])
        rtn["temps"].append(s[1])
    return rtn

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
    print(f"\nclient ip: {request.remote_addr}\nreceived form: {request.json}\n")
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
    if request.remote_addr == '192.168.100.12':
        global data, history
        int_t = int(time.time() + (3600 * TIMEZONE))
        t = time.gmtime(int_t)
        if t.tm_hour == 0 and t.tm_minute <= 1:
            history = []
        data = request.json
        if not data["success"]:
            return app.response_class(
            response="ERROR",
            status=404,
            content_type='text/plain',
            headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"},
        )
        for val in data['values']:
            print(val, file=sys.stderr)
            new = True 
            for i in range(len(history)):
                if history[i]["name"] == val["name"]:
                    history[i]["temps"].append(val["value"])
                    history[i]["times"].append(data["clock"])
                    new = False
            if new == False:
                continue
            
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
    old = load_old()
    history.append({"name": config[0]["id"], "temps": old["temps"], "times": old["times"]})
    app.run(debug=DEBUG_MODE, host='0.0.0.0')
