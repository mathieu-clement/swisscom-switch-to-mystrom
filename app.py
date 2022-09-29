#!/usr/bin/env python3.9

from flask import Flask, request, Response
import json
import os
import subprocess

real_host = os.environ['REAL_HOST']
listen_host = os.environ['LISTEN_HOST']
listen_port = os.environ['LISTEN_PORT']

app = Flask(__name__)

def fetch(path):
    url = 'http://' + real_host + path

    # The host refuses anything with the "Accept-Encoding" header
    # and I couldn't find a way to prevent the HTTP libraries in Python
    # to send them.
    # Curl, in comparison, does not send it by default.

    process = subprocess.Popen(['curl', '--location', '-s', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8')


@app.route("/api/v1/info")
def info():
    resp = json.loads(fetch('/api/v1/info'))
    return resp

@app.route("/info.json")
def info_json():
    resp = json.loads(fetch('/api/v1/info'))
    return resp

@app.route("/report")
def report():
    resp = json.loads(fetch('/report'))
    relay = resp['relay']
    return {
       'relay': relay,
       'power': 1.00,
       'Ws': 1.00,
       'temperature': 0.00
    }

@app.route("/relay")
def relay():
    state = request.args.get('state')
    if state != '0' and state != '1':
        raise 'Invalid state'
    fetch('/relay?state=' + state)
    return 'OK'

if __name__ == '__main__':
    app.run(host=listen_host, port=listen_port)
