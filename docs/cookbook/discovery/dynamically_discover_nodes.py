import networkzero as nw0

#
# On Machine A
#
nw0.advertise("cluster/a")
#
# On Machine B
#
nw0.advertise("cluster/b")

#
# On the cluster master
#
nodes = set(nw0.discover_group("cluster"))
old_nodes = nodes

#
# On Machine C
#
nw0.advertise("cluster/c")
#
# Machine A stops and its advert expires
#

#
# On the cluster master
#
nodes = set(nw0.discover_group("cluster"))
for name, address in old_nodes - nodes:
    print("%s has left the cluster" % name)
for name, address in nodes - old_nodes:
    print("%s has joined the cluster" % name)
