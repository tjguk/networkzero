import networkzero as nw0

ip_address = "192.0.2.1"
address = nw0.advertise("myservice", ip_address)
print("Service is at", address)