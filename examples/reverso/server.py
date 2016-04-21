import networkzero as nw0

address = nw0.advertise("reverso")
while True:
    message = nw0.wait_for_message_from(address)
    nw0.send_message_to(address, message[::-1])
