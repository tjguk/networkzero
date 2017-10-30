import networkzero as nw0

news = nw0.discover("blink_news")
while True:
    topic, message = nw0.wait_for_news_from(news, "BLINK")
    print(message)
