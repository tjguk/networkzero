import networkzero as nw0

nw0.advertise("abc")
nw0.advertise("def")
services = nw0.discover_all()
print("Services:", services)
