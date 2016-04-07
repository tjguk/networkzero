import networkzero as nw0

address = nw0.advertise("service")
message = nw0.wait_for_message(address)
print("Message received: ", message)
nw0.send_reply(address, "Received: %s" % message)
