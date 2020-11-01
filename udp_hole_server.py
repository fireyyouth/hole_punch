import socket
from threading import Thread, Lock
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
import collections
import time
import json
import os
import traceback

HEARTBEAT_INTERVAL = 3

online = {}
time_index = collections.OrderedDict()
mutex = Lock()

def clear_expired():
    global online, time_index, mutex
    try:
        while True:
            now = time.time()
            poped = False
            with mutex:
                while len(time_index):
                    t = next(iter(time_index))
                    if t >= now:
                        break
                    for addr in time_index[t]:
                        online.pop(addr)
                    time_index.pop(t)
                    poped = True
            if poped:
                print('clear_expired():', online, time_index)
            time.sleep(1)
    except:
        traceback.print_exc()
        os._exit(1)


class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global online
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        r = []
        for key in online:
            r.append({'ip' : key[0], 'port' : key[1]})
        self.wfile.write(json.dumps(r).encode())

def httpd():
    try:
        HTTPServer(('', 9999), MyHTTPHandler).serve_forever()
    except:
        traceback.print_exc()
        os._exit(1)



def track():
    global online, time_index, mutex
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('0.0.0.0', 9999))
        while True:
            data, addr = s.recvfrom(128)

            new_time = time.time() + HEARTBEAT_INTERVAL

            with mutex:
                if addr in online:
                    old_time = online[addr]
                    time_index[old_time].remove(addr)
                    if len(time_index[old_time]) == 0:
                        time_index.pop(old_time)

                online[addr] = new_time

                if new_time in time_index:
                    time_index[new_time].add(addr)
                else:
                    time_index[new_time] = {addr}

            print('track():', online, time_index)
    except:
        traceback.print_exc()
        os._exit(1)

back_jobs = [
        Thread(target=clear_expired),
        Thread(target=httpd),
        Thread(target=track),
]

for job in back_jobs:
    job.start()

for job in back_jobs:
    job.join()
