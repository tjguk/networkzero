import networkzero as nw0

address = nw0.advertise("reverso")
while True:
    message = nw0.wait_for_message(address, wait_for_secs=10)
    if message is not None:
        nw0.send_reply(address, message[::-1])
