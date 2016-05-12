.. currentmodule:: discovery
.. highlight:: python
   :linenothreshold: 1

Using the discovery module
==========================

The examples here all refer to the :mod:`discovery` module.

In the context of networkzero, an address is a string combining an
IP address and a port, eg "192.0.2.1:12345". You can specify just
the IP address, just the port, both or neither, depending on how
much control you want.

Advertise a service
-------------------

.. literalinclude:: discovery/advertise_a_service.py
   
Discussion
~~~~~~~~~~
If you are running a service in one process, advertising it will enable
other processes and machines to know what address to connect to. This
example shows the minimum you need supply -- just a name -- to advertise
a service. If you haven't chosen an address, one will be returned which
you can then use to send and receive messages.

Advertise a service with a specific address
-------------------------------------------

.. literalinclude:: discovery/advertise_a_service_with_a_specific_address.py

Discussion
~~~~~~~~~~
If you know exactly what address you want to use for your service, you can
specify that when advertising. In this example, no port is given so one
will be selected at random from the range of ports designated as dynamic.
   
Advertise a service with a specific port
----------------------------------------

.. literalinclude:: discovery/advertise_a_service_with_a_specific_port.py

Discussion
~~~~~~~~~~
It may be that you've agreed a particular port to work with, regardless
of the network you're on. In that case, you can supply just a port number
and a suitable IP address will be supplied by networkzero.

Advertise a service with a wildcard address
-------------------------------------------

.. literalinclude:: discovery/advertise_a_service_with_a_wildcard_address.py

Discussion
~~~~~~~~~~
Sometimes the machine you're on has several IP addresses, for example when
it is connected to to a wireless and to a wired network, or when it supports
a virtual machine. Most of the time, networkzero will select the best address
but if it doesn't you can specify which of the networks you want to use.

Note that this doesn't mean you have to specify the entire IP address, merely
enough of it to distinguish one network from another.

Discovering a service
---------------------

.. literalinclude:: discovery/discover_a_service.py
   
Discussion
~~~~~~~~~~
Once a service has been advertised by name, that name can be discovered by any
other networkzero program on the same network. You only need to know the name
used. Discovery will wait for up to 60 seconds for a service to be advertised.
If one is discovered, its address string is returned; if not, `None` is
returned.

Discover all services
---------------------

.. literalinclude:: discovery/discover_all_services.py

Discussion
~~~~~~~~~~
It can be useful to see what services are advertised across the whole
network. This can be used, for example, in a chat room to discover new
members joining the room. Pairs of names and addresses are returned, suitable
for converting into a Python dictionary.

Discover a group of services
----------------------------

.. literalinclude:: discovery/discover_group.py

Discussion
~~~~~~~~~~
By adopting a common convention, it is possible to group advertised services
together. This could be used, as in this example, to identify all members of
a particular chat session. Or -- in a classroom or club situation -- to have
teams identify their own services so as not to confuse them with other team's
services of the same name. 

Use a different separator for a group of services
-------------------------------------------------

.. literalinclude:: discovery/discover_group_colon.py

Discussion
~~~~~~~~~~
Perhaps it's not convenient to use the "/" character to separate the group
from the service name. You can use any character to separate the parts of
the name. Then you specify that character when you call `discover_group`.

Dynamically Discover Nodes
--------------------------

.. literalinclude:: discovery/dynamically_discover_nodes.py

Discussion
~~~~~~~~~~
A cluster is a group of computers working together. Each computer registers
a service called "cluster/X" where "X" is the computer's name. If that
machine stops running, its advert will time out and no longer be available.

The computer which is co-ordinating the cluster checks every so often to
see which computers have left the cluster and which have joined.
