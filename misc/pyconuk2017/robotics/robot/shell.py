#!python3
import os, sys
import shlex

import zmq

from . import config

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://%s:%s" % (config.LISTEN_ON_IP, config.LISTEN_ON_PORT))

    while True:
        command = input("Command: ")
        socket.send(command.encode(config.CODEC))
        response = socket.recv().decode(config.CODEC)
        print("  ... %s" % response)
        words = shlex.split(response.lower())
        status = words[0]
        if len(words) > 1:
            info = words[1:]
        if status == "finished":
            print("Finished status received from robot")
            break

if __name__ == '__main__':
    main(*sys.argv[1:])
