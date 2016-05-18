import os, sys
import networkzero as nw0

try:
    input = raw_input
except NameError:
    pass

gallery = nw0.discover("gallery")
filepath = input("Filename: ")
filename = os.path.basename(filepath)
with open(filepath, "rb") as f:
    data = f.read()
    
nw0.send_message_to(gallery, (filename, nw0.bytes_to_string(data)))
