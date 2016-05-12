import networkzero as nw0

nw0.advertise("myservice")
myservice = nw0.discover("myservice")
print("myservice is at", myservice)