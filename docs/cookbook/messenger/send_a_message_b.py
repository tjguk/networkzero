import networkzero as nw0

service = nw0.discover("service")
nw0.send_message_to(service, "This is a message")
reply = nw0.wait_for_message_from(service)
print("Reply: ", reply)

