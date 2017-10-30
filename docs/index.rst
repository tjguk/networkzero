NetworkZero
===========

NetworkZero makes it easier to use Python to connect things together
across the internet. It's especially focused on the classroom
or club situation where short-lived programs need to discover
each other on the same or a different computer without having to
know IP addresses or hostnames.

It runs on Python 2.7 and Python 3.3+ and should run anywhere that 
Python runs. In particular, it's tested automatically on Windows,
Mac and Linux, and is used on Raspberry Pi.

NetworkZero offers two main services:

    * Discovering short-lived and ad hoc programs
    * Sending simple Python objects between programs

What can I use it for?
----------------------

Anything which can make use of one machine or process to talk to 
another across a network. For example:

    * Sending commands to a robot
    * Sending data from an RPi with a sensor to a graphing PC and a 
      long-term storage log
    * Showing the state of a shared game in one window while sending 
      commands from another.

Can you give me an example?
---------------------------

[Machine or Process A]::

    import networkzero as nw0

    address = nw0.advertise("hello")
    while True:
        name = nw0.wait_for_message_from(address)
        nw0.send_reply_to(address, "Hello " + name)

[Machine or Process B and C and D ...]::

    import networkzero as nw0
    
    hello = nw0.discover("hello")
    reply = nw0.send_message_to(hello, "World!")
    print(reply)
    reply = nw0.send_message_to(hello, "Tim")
    print(reply)

This runs a service, advertised under the name "hello"
which will send back "Hello <name>" whenever <name> is sent to it.
Other machines or processes discover the service and send
names to it, receiving a greeting in return.

Read More
---------

.. toctree::
   :maxdepth: 2
   
   installation
   usage
   for-teachers
   for-developers
