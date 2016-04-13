import sys
import random
import time
import traceback
import uuid

import networkzero as nw0

words = {}
with open("words.txt") as f:
    for word in f:
        words.setdefault(word[0], []).append(word.strip())

my_name = "halifax/" + uuid.uuid4().hex
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
addresses = [address for (name, address) in nw0.discover_group("halifax") if name != my_name]
print(addresses)

while True:
    
    if first_word:
        word = first_word
        first_word = None
    else:
        print("Waiting for next word...")
        word = nw0.wait_for_message(my_address, autoreply=True)

    print("Got word", word)
    candidate_words = words[word[-1]]
    random.shuffle(candidate_words)
    next_word = candidate_words.pop()
    
    print("Sending word", next_word)
    nw0.send_message(addresses, next_word)
