# -*- coding: utf-8 -*-
import os, sys
print(sys.version_info)
import json
import select
import socket
import time

def _unpack(message):
    return json.loads(message.decode("utf-8"))

def _pack(message):
    return json.dumps(message).encode("utf-8")
    
IP_ADDRESS = "192.168.1.255"
PORT = 9999
MESSAGE_SIZE = 256
message = _pack("Hello")
    
#
# Set the socket up to broadcast datagrams over UDP
#
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(("", PORT))

while True:
    print("Sending", message)
    s.sendto(message, 0, (IP_ADDRESS, PORT))
    time.sleep(3)
