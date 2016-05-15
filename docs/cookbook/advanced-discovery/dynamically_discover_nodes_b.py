import networkzero as nw0

name = "B"

nw0.advertise("cluster/%s" % name)
master = nw0.discover("cluster/master")

while True:
    command = nw0.wait_for_message_from(master, autoreply=True)
    #
    # Do useful things until told to stop
    #
    if command == "STOP":
        break
