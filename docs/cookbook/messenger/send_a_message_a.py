import networkzero as nw0

address = nw0.advertise("service")
message = nw0.wait_for_message_from(address)
print("Message received: ", message)
nw0.send_message_to(address, "Received: %s" % message)
