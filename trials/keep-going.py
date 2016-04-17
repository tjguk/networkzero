try:
    import queue
except ImportError:
    import Queue as queue
import threading
import time
import uuid

import networkzero as nw0

def do(finish_at, number=None):
    collector = nw0.discover("collector")
    group = "keep-going"
    name = "%s/%s" % (group, uuid.uuid4().hex)
    address = nw0.advertise(name)
    time.sleep(3)
    
    neighbours = [address for name, address in nw0.discover_group(group, exclude=[name])]
    print("Neighbours:", neighbours)

    while True:
        if number is not None:
            nw0.send_message(collector, (name, number))
            nw0.send_message(neighbours, number + 1)
        number = nw0.wait_for_message(address, autoreply=True)
        if number > finish_at:
            break

def main(n_threads=4, finish_at=1000):
    collector = nw0.advertise("collector")
    threads = []
    for n in range(n_threads):
        threads.append(threading.Thread(target=do, args=(finish_at, 1 if n == 0 else None)))
    for thread in threads:
        thread.setDaemon(True)
        thread.start()
    
    collected = {}
    while True:
        name, number = nw0.wait_for_message(collector, autoreply=True)
        collected.setdefault(name, set()).add(number)
        print(name, number)
        if number >= finish_at:
            break
    
    print("All numbers collected; joining threads")
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()