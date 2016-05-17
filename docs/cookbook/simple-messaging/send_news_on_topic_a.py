import networkzero as nw0
import random
import time

address = nw0.advertise("news2")

#
# In lieu of an actual temperature sensor!
#
temperatures = range(15, 20)
humidities = range(0, 100)
while True:
    temperature = random.choice(temperatures) + random.random()
    humidity = random.choice(humidities)
    nw0.send_news_to(address, "temperature", temperature)
    time.sleep(random.random())
    nw0.send_news_to(address, "humidity", humidity)
    time.sleep(random.random())
