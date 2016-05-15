import networkzero as nw0

name = "cluster/master"
address = nw0.advertise(name)

#
# On the cluster master
#
nodes = set(nw0.discover_group("cluster", exclude=name))
old_nodes = nodes
print("Nodes:", ", ".join(nodes))

#
# Send a command to A .... which will unaccountably fail
#
node_a = nw0.discover("cluster/A")
nw0.send_message_to(node_a, "STOP")

#
# Wait a few seconds for node C to wake up
#
time.sleep(5)

#
# On the cluster master
#
nodes = set(nw0.discover_group("cluster"))
for name, address in old_nodes - nodes:
    print("%s has left the cluster" % name)
for name, address in nodes - old_nodes:
    print("%s has joined the cluster" % name)

for name, address in nodes:
    nw0.send_message_to(address, "STOP")
