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
        services = [address for (name, address) in nw0.discover_all() if name != my_name]

        topic, message = nw0.wait_for_notification(services, "quote", wait_for_s=0)
        if topic:
            incoming_name, incoming_quote = message
            print("%s says: %s" % (incoming_name, incoming_quote))
        
        quote = random.choice(quotes)
        nw0.send_notification(my_address, "quote", (my_name, quote))
        
        time.sleep(1)

if __name__ == '__main__':
    main(*sys.argv[1:])
