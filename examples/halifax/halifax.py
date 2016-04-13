import sys
import random
import time
import traceback
import uuid

import zmq
context = zmq.Context()

import networkzero as nw0

words = {}
with open("words.txt") as f:
    for word in f:
        words.setdefault(word[0], []).append(word.strip())

my_name = uuid.uuid4().hex
my_address = nw0.advertise(my_name)
if len(sys.argv) == 2:
    first_word = sys.argv[1].lower().strip()
else:
    first_word = ''

#
# Wait 30 seconds to discover all neighbours
#
print("Waiting for neighbours to show up...")
time.sleep(10)

print("Looking for neighbours")
addresses = [address for (name, address) in nw0.discover_all() if name != my_name]
print(addresses)

listening_socket = context.socket(zmq.REP)
listening_socket.bind("tcp://%s" % my_address)

sending_socket = context.socket(zmq.REQ)
for address in addresses:
    sending_socket.connect("tcp://%s" % address)

try:
    while True:
        
        if first_word:
            word = first_word
            first_word = None
        else:
            print("Waiting for next word...")
            word = listening_socket.recv().decode("utf-8")
            listening_socket.send(word.encode("utf-8"))

        print("Got word", word)
        candidate_words = words[word[-1]]
        random.shuffle(candidate_words)
        next_word = candidate_words.pop()
        
        print("Sending word", next_word)
        sending_socket.send(next_word.encode("utf-8"))
        sending_socket.recv().decode("utf-8")
except:
    traceback.print_exc()
    input("Press enter...")
    