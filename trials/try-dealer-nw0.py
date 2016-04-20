import networkzero as nw0

import uuid

a1 = "127.0.0.1:5000"
a2 = "127.0.0.1:5001"

d1 = uuid.uuid4().hex
d2 = uuid.uuid4().hex

print("About to send %s to %s" % (d1, a1))
nw0.send_message(a1, d1)
print("About to receive on s2")
data1 = nw0.wait_for_message(a1)
print(data1)
assert data1 == d1
nw0.send_reply(a1, d2)
data2 = nw0.wait_for_message(a1)
print(data2)
assert data2 == d2