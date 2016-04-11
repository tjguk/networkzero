import sys
print(sys.version_info)
import random
import time

import networkzero as nw0

quotes = [
    "Humpty Dumpty sat on a wall",
    "Hickory Dickory Dock",
    "Baa Baa Black Sheep",
    "Old King Cole was a merry old sould",
]

my_name = input("Name: ")
nw0.advertise(my_name)

while True:
    services = [(name, address) for (name, address) in nw0.discover_all() if name != my_name]
    
    for name, address in services:
        topic, message = nw0.wait_for_notification(address, "quote", wait_for_s=0)
        if topic:
            print("%s says: %s" % (name, message))
        quote = random.choice(quotes)
        nw0.send_notification(address, "quote", quote)
    
    time.sleep(0.5)
