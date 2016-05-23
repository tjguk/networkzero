from __future__ import print_function
import networkzero as nw0

try:
    # Python 2.7 compat
    input = raw_input
except NameError:
    pass

service = nw0.discover("anagram")
while True:
    anagram = input("Enter anagram: ")
    word = nw0.send_message_to(service, anagram)
    if word:
        print(word)
    else:
        print("Nothing found")
