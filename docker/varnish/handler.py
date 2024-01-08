#!/usr/bin/env python

import signal
import subprocess
import sys
from time import sleep

command = sys.argv[1]

keep = True
process = None
restart = False


def hup_handler(signum, frame):
    global restart
    restart = True
    print("SIGHUP received - scheduling restart")
    process.send_signal(signal.SIGTERM)


def propagate_handler(signum, frame):
    global restart
    restart = False
    # print("propagating %s" % signum)
    process.send_signal(signum)


for sig in (signal.SIGTERM, signal.SIGINT):
    signal.signal(sig, propagate_handler)

signal.signal(signal.SIGHUP, hup_handler)

while keep:
    # print('starting')
    keep = False
    process = subprocess.Popen(command, shell=True)
    process.wait()
    if restart:
        print("restarting service")
        keep = True
        restart = False
