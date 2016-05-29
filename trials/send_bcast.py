#!python3
import os, sys
import socket
import time

def run(message=""):
    if not message:
        message = input("Message: ")
    bmessage = message.encode("utf-8")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    while True:
        s.sendto(bmessage, ('192.168.1.255', 53005))
        time.sleep(1)

if __name__ == '__main__':
    run(*sys.argv[1:])
