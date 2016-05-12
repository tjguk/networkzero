import networkzero as nw0

alice = nw0.advertise("chat/alice")
bob = nw0.advertise("chat/bob")
doug = nw0.advertise("chat/doug")
services = dict(nw0.discover_group("chat"))

print(services)