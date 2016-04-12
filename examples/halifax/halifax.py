import random
import time

import zmq
context = zmq.Context()

import networkzero as nw0

words = {}
with open("words.txt") as f:
    for word in f:
        words.setdefault(word[0], []).append(word.strip())

my_name = input("Name: ")
my_address = nw0.advertise(my_name)
first_word = input("Word: ").strip()

while True:
    
    services = sorted(nw0.discover_all())
    if len(services) < 2:
        continue
    
    print("Looking for neighbours")
    for n, (name, address) in enumerate(services):
        if name == my_name:
            left_name, left_address = services[n - 1]
    
    print(left_name, left_address)

    time.sleep(1)
    if first_word:
        word = first_word
        first_word = None
    else:
        print("Waiting for left neighbour")
        with context.socket(zmq.REP) as socket:
            socket.connect("tcp://%s" % left_address)
            word = socket.recv().decode("utf-8")
            socket.send(b"OK")

    print("Got word", word)
    candidate_words = words[word[-1]]
    random.shuffle(candidate_words)
    next_word = candidate_words.pop()
    print("Next word is", next_word)

    time.sleep(1)
    with context.socket(zmq.REQ) as socket:
        socket.bind("tcp://%s" % my_address)
        ok = socket.send(next_word.encode("utf-8"))
