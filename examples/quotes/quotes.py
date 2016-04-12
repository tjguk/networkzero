import sys
print(sys.version_info)
import random
import time

import networkzero as nw0

with open("quotes.txt") as f:
    quotes = [line.strip() for line in f]

def main(address_pattern=None):
    my_name = input("Name: ")
    my_address = nw0.advertise(my_name, address_pattern)
    print("Advertising %s on %s" % (my_name, my_address))

    while True:
        services = [(name, address) for (name, address) in nw0.discover_all() if name != my_name]

        for name, address in services:
            topic, message = nw0.wait_for_notification(address, "quote", wait_for_s=0)
            if topic:
                print("%s says: %s" % (name, message))
        
        quote = random.choice(quotes)
        nw0.send_notification(my_address, "quote", quote)
        
        time.sleep(1)

if __name__ == '__main__':
    main(*sys.argv[1:])
