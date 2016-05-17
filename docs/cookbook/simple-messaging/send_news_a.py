import networkzero as nw0
import random
import time

address = nw0.advertise("news1")

#
# In lieu of an actual temperature sensor!
#
temperatures = range(15, 20)
while True:
    temperature = random.choice(temperatures) + random.random()
    nw0.send_news_to(address, "temperature", temperature)
    time.sleep(1.0)
