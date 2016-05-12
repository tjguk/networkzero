import networkzero as nw0

nw0.advertise("myservice7")
nw0.advertise("myservice8")
services = nw0.discover_all()
print("Services:", services)
