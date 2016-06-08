.. currentmodule:: discovery
.. highlight:: python
   :linenothreshold: 1

Advertise & Discover Services: Advanced Usage
=============================================

The examples here all refer to the :mod:`networkzero.discovery` module.


Discover a group of services
----------------------------

On machine A
~~~~~~~~~~~~
.. literalinclude:: advanced-discovery/discover_group_a.py

On machine B
~~~~~~~~~~~~
.. literalinclude:: advanced-discovery/discover_group_b.py

On machine C
~~~~~~~~~~~~
.. literalinclude:: advanced-discovery/discover_group_c.py

Discussion
~~~~~~~~~~
By adopting a common convention, it is possible to group advertised services
together. This could be used, as in this example, to identify all members of
a particular chat session. Or---in a classroom or club situation---to have
teams identify their own services so as not to confuse them with other team's
services of the same name. 

Use a different separator for a group of services
-------------------------------------------------

.. literalinclude:: advanced-discovery/discover_group_colon.py

Discussion
~~~~~~~~~~
Perhaps it's not convenient to use the "/" character to separate the group
from the service name. You can use any character to separate the parts of
the name. Then you specify that character when you call `discover_group`.


Dynamically discover services
-----------------------------

Node A
~~~~~~
.. literalinclude:: advanced-discovery/dynamically_discover_nodes_a.py

Node B
~~~~~~
.. literalinclude:: advanced-discovery/dynamically_discover_nodes_b.py

Node C
~~~~~~
.. literalinclude:: advanced-discovery/dynamically_discover_nodes_c.py

Master
~~~~~~
.. literalinclude:: advanced-discovery/dynamically_discover_nodes_master.py

Discussion
~~~~~~~~~~
A cluster is a group of computers working together. Each computer registers
a service called "cluster/X" where "X" is the computer's name. If that
machine stops running, its advert will time out and no longer be available.

The computer which is co-ordinating the cluster checks every so often to
see which computers have left the cluster and which have joined.
