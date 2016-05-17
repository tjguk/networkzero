import networkzero as nw0

service = nw0.discover("messenger2")

nw0.send_message_to(service, "This is a command")
