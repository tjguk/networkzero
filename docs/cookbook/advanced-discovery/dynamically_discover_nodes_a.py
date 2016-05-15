import networkzero as nw0

name = "A"

nw0.advertise("cluster/%s" % name)
master = nw0.discover("cluster/master")

while True:
    command = nw0.wait_for_message_from(master, autoreply=True)

    #
    # ... something goes wrong
    #
    raise RuntimeError
