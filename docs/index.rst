NetworkZero
===========

NetworkZero makes it easier to use Python to connect things together 
across the. It's especially focused on the classroom 
or club situation where short-lived programs need to discover 
each other on the same or a different computer without having to 
know IP addresses or hostnames.

It offers two main services:

    * A means of discovering short-lived and ad hoc programs
    * A way to send simple Python objects between those programs

What can I use it for?
----------------------

Anything which needs one machine or process to talk to another 
across a network. For example:

    * Sending commands to a robot
    * Sending data from an RPi with a sensor to a graphing PC and a long-term storage log
    * Showing the state of a shared game in one window while sending commands from another.

Can you give me an example?
---------------------------

[Machine or Process A]::

    import networkzero as nw0

    address = nw0.advertise("hello")
    while True:
        name = nw0.wait_for_message(address)
        nw0.send_reply(address, "Hello " + name)

[Machine or Process B and C and D ...]::

    import networkzero as nw0
    
    hello = nw0.discover("hello")
    print(nw0.send_message("World!"))
    print(nw0.send_message("Tim"))

This runs up a service, advertised under the name "hello"
which will send back "Hello <name>" whenever <name> is sent to it.
Other machines or processes discover that service and send
names to it, receiving a greeting in return.

Read More
---------

.. toctree::
   :maxdepth: 2
   
   intro
   for-teachers
   for-students
   for-developers
