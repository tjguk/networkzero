import networkzero as nw0

service = nw0.discover("messenger1")

reply = nw0.send_message_to(service, "This is a message")
print("Reply: ", reply)
