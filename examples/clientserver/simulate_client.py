import networkzero as nw0

hello = nw0.discover("hello")
reply = nw0.send_message_to(hello, "World!")
print(reply)
reply = nw0.send_message_to(hello, "Tim")
print(reply)
