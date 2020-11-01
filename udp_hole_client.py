import socket
from threading import Thread
import time
import requests
import os
import traceback

REMOTE_ADDR = ('34.84.245.193', 9999)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s.bind(('0.0.0.0', 12345))

def heartbeat():
    global s
    try:
        while True:
            s.sendto(b'!', REMOTE_ADDR)
            time.sleep(1)
    except:
        traceback.print_exc()
        os._exit(1)

def greet():
    global s
    try:
        while True:
            rsp = requests.get('http://{}:{}'.format(*REMOTE_ADDR))
            for item in rsp.json():
                peer = (item['ip'], item['port'])
                s.sendto(b'hello', peer)
            time.sleep(1)
    except:
        traceback.print_exc()
        os._exit(1)

def receive():
    global s
    try:
        while True:
            data, addr = s.recvfrom(128)
            print('received', data, addr)
    except:
        traceback.print_exc()
        os._exit(1)

back_jobs = [
        Thread(target=heartbeat),
        Thread(target=greet),
        Thread(target=receive),
        ]

for job in back_jobs:
    job.start()

for job in back_jobs:
    job.join()

