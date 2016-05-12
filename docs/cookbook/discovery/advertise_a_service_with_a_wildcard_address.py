import networkzero as nw0

ip_address = "127.*"
address = nw0.advertise("myservice4", ip_address)
print("Service is at", address)
