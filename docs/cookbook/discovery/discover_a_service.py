import networkzero as nw0

nw0.advertise("myservice5")
myservice = nw0.discover("myservice5")
print("myservice is at", myservice)