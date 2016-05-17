import networkzero as nw0

addresses = [address for name, address in nw0.discover_group("movement")]

while True:
    topic, (sensor, is_movement) = nw0.wait_for_news_from(addresses)
    if is_movement:
        print("Movement from %s!!!" % sensor)
