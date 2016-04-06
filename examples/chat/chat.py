import networkzero as nw0

name = input("Name: ")
address = nw0.advertise(name)
while True:
    message = input("Message: ")
    nw0.send_notification(address, "chat", message)
