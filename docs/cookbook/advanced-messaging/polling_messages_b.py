import time
import networkzero as nw0

service = nw0.discover("poller1")

time.sleep(3)
reply = nw0.send_message_to(service, "This is a message")
print("Reply: ", reply)
