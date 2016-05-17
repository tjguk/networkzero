import networkzero as nw0

address = nw0.advertise("messenger1")

message = nw0.wait_for_message_from(address)
print("Message received: ", message)
nw0.send_reply_to(address, "Received: %s" % message)
