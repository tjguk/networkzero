import networkzero as nw0

address = nw0.discover("news1")

while True:
    topic, temperature = nw0.wait_for_news_from(address)
    print("Temperature is:", temperature)
