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
    
PORT = 9999
MESSAGE_SIZE = 256
    
#
# Set the socket up to broadcast datagrams over UDP
#
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(("192.168.31.2", PORT))

print("Listening...")
while True:
    rlist, wlist, xlist = select.select([s], [], [], 1)
    if s in rlist:
        message, source = s.recvfrom(MESSAGE_SIZE)
        service_name, service_address = _unpack(message)
        print("%s: Found %s at %s" % (time.asctime(), service_name, service_address))
