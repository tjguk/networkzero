import zmq
import uuid

address = "tcp://127.0.0.1:5001"

c = zmq.Context()
s1 = c.socket(zmq.DEALER)
s2 = c.socket(zmq.DEALER)
s3 = c.socket(zmq.DEALER)

d1 = uuid.uuid4().hex.encode("utf-8")
d2 = uuid.uuid4().hex.encode("utf-8")
d3 = uuid.uuid4().hex.encode("utf-8")

#~ p = zmq.Poller()
#~ p.register(s1, zmq.POLLIN)
#~ p.register(s2, zmq.POLLIN)

print("About to bind to", address)
s2.bind(address)
print("About to connect to", address)
s1.connect(address)
s3.connect(address)

print("About to send %s from s1" % d1)
s1.send(d1)
print("About to send %s from s3" % d3)
s3.send(d3)

print("About to receive on s2")
data1 = s2.recv()
print(data1)
assert data1 == d1
data3 = s2.recv()
print(data3)
assert data3 == d3


print("About to send %s from s1" % d2)
s1.send(d2)
print("About to receive on s2")
data2 = s2.recv()
print(data2)
assert data2 == d2

print("About to reply %s from s2" % data1)
s2.send(data1)
print("Checking for reply on s1")
print(s1.recv())

print("About to reply %s from s2" % data2)
s2.send(data2)
print("Checking for reply on s1")
print(s1.recv())
