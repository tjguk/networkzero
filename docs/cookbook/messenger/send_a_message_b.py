import networkzero as nw0

service = nw0.discover("service")
reply = nw0.send_message(service, "This is a message")
print("Reply: ", reply)

