import networkzero as nw0

address = nw0.discover("news2")

while True:
    topic, humidity = nw0.wait_for_news_from(address, "humidity")
    print("Humidity is:", humidity)
