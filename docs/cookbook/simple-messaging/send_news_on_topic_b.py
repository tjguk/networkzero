import networkzero as nw0

address = nw0.discover("news2")

while True:
    topic, temperature = nw0.wait_for_news_from(address, "temperature")
    print("Temperature is:", temperature)
