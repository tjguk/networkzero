import os, sys
import select
import socket 

port = 53005  # where do you expect to get a msg?
bufferSize = 1024 # whatever you need

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', port))
s.setblocking(0)

while True:
    result = select.select([s],[],[], 2.0)
    if result[0]:
        msg = result[0][0].recv(bufferSize) 
        print(msg)