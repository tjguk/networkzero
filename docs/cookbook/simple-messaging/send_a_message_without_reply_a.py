import networkzero as nw0

address = nw0.advertise("messenger2")

message = nw0.wait_for_message_from(address, autoreply=True)
print("Message received: ", message)
