from flask import Flask, request, jsonify
from json import dumps, loads
from threading import Thread
import requests
from probe import *
import logging



class _Bouncer:
    def __init__(self, app, callback=None, inport=None, outport=None):
        self.callback = callback
        self.inport = inport
        self.outport = outport
        self.data = {}
        self.partners = {}
        self.app = app

    def start(self, ips, data, bounces):
        self.check_params()
        self.partners = {ip:0 for ip in ips}
        for ip in ips:
            assert self.probe(ip)

        logging.info("Starting.")
        logging.info("Broadcasting to ips: %s", str(ips))
        logging.info("Total bounces: %d", bounces)

        for ip in self.partners:
            json_data = {
                'data': data[ip],
                'generations': bounces,
                'init': 1
            }
            self.post_request(ip, self.outport, json_data)
        self.wait()

    def branch_back(self, generations):
        x = Thread(target=lambda x: self.bounce_back(x), args=(generations,))
        x.start()

    def bounce_back(self, generations):
        #this should return a json-like dictionary object with 2 fields: "data" and "generations"
        self.check_params()
        return_data = self.callback(self.data)

        #KEEEP GENERATIONS IN SELF>DATA

        if generations > 0:
            assert isinstance(return_data, dict)
            assert set(return_data.keys())==set(self.partners.keys())

            for ip in self.partners:
                return_json = {
                    'data': return_data[ip],
                    'generations': generations-1
                }
                logging.info("Sending response to %s", ip)
                logging.info("%d bounces left.", generations-1)

                response = requests.post('http://' + ip + ':' + str(self.outport) + '/bounce',
                                        json = dumps(return_json))
                if not(response.ok):
                    raise RuntimeError("Request failed: status code = ", response.status_code)
        self.data = {}

    def post_request(self, ip, port, data):
        response = requests.post('http://' + ip + ':' + str(port) + '/bounce', json = dumps(data))
        if not(response.ok):
            raise RuntimeError("Request failed: status code = ", response.status_code)

    def probe(self, ip):
        self.check_params()
        ip = 'http://' + ip + ':' + str(self.outport) + '/probe'
        print('Probing: '+ip+'...', end='')
        response = requests.get(ip)
        if response.json()['ok']==1:
            print('Success!')
            return True
        else:
            return False

    def check_params(self, params={'callback': 'function', 'inport': int, 'outport': int}):
        undefined = []
        for param in params:
            if isinstance(params[param], str):
                if not (callable(getattr(self, param))):
                    undefined.append(param)
            else:
                if not (isinstance(getattr(self, param), params[param])):
                    undefined.append(param)

        if len(undefined)>0:
            raise(ValueError("Required attributes not defined, please define them with 'bouncer.attr = ...' :"
                                + ", ".join(undefined)))

    def wait(self):
        self.check_params()
        self.app.run(port=self.inport, host='0.0.0.0')


app = Flask(__name__)

bouncer = _Bouncer(app)

@app.route("/bounce", methods = ["POST"])
def bounce():
    request_json=loads(request.json)
    ip = request.remote_addr
    if ip not in bouncer.partners:
        if "init" not in request_json:
            raise RuntimeError('Unexpected request from ', request.remote_addr)
        else:
            assert request_json['init']==1

    bouncer.partners[request.remote_addr] = 1
    bouncer.data[ip] = request_json['data']

    #NEED TO SPAWN NEW THREAD OR SOMEHOW CLOSE CONNECTION AFTER RECEIVING DATA

    logging.info('Bounce caught from %s', ip)
    logging.info('Received %d/%d requests', len(bouncer.data), len(bouncer.partners))
    if 0 not in bouncer.partners.values():
        bouncer.branch_back(generations = request_json['generations'])
        for partner in bouncer.partners:
            bouncer.partners[partner] = 0
    return jsonify({'ok': 1})

@app.route('/probe', methods = ['GET'])
def receive_probe():
    return jsonify({'ok': 1})

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")
