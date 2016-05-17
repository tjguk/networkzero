import networkzero as nw0
import random
import time
import uuid

name = "movement/%s" % uuid.uuid1().hex
address = nw0.advertise(name)
print("Sending from %s -> %s" % (name, address))

#
# In lieu of an actual sensor!
#
while True:
    is_movement = random.random() > 0.5
    nw0.send_news_to(address, "movement", (name, is_movement))
    time.sleep(random.random())
