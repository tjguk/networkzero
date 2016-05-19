import time
import networkzero as nw0

address = nw0.advertise("poller1")

while True:
    message = nw0.wait_for_message_from(address, wait_for_s=0)
    if message is not None:
        print("Received:", message)
        nw0.send_reply_to(address, "Received: %s" % message)
        break
    else:
        print("Doing other useful things ...")
        time.sleep(1)
