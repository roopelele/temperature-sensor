from flask import Flask, send_file, request, redirect, json
from flask_cors import CORS, cross_origin
import time
import json
import sys
import os

FOLDER = "/home/pi/temperature"
TIMEZONE = 2
data = {}
history = []

app = Flask(__name__)
cors = CORS(app)

def load_config():
    with open("config.json", 'r') as infile:
        return json.load(infile)

@app.route('/update/', methods=['POST'])
def update_data():
    print(f"client ip: {request.remote_addr}\nreceived form: {request.json}\n")
    if request.remote_addr == '192.168.100.12':
        global data, history
        int_t = int(time.time() + (3600 * TIMEZONE))
        t = time.gmtime(int_t)
        if t.tm_hour == 0 and t_tm_minute < 5:
            history = []
        data = request.json
        history.append(data)
    return redirect('/current/')

@app.route('/current/', methods=['GET'])
def get_current_data():
    d = {'config': config, 'data': data}
    response = app.response_class(
        response=json.dumps(d),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/history/')
def get_history():
    d = {'config': config, 'data': history}
    response = app.response_class(
        response=json.dumps(d),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/config/')
def get_config():
    response = app.response_class(
        response=json.dumps(config),
        status=200,
        mimetype='application/json'
    )
    return response


config = load_config()

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
