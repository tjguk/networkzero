NetworkZero
===========

..  note::

    **10th April 2016** This is under heavy development at the moment; things
    can and will change, possibly quite radically, over the next few days 
    and weeks. Please do take it for a spin, but don't base any long-term
    plans on the current API. TJG

    **21st April 2016** Still a lot of development going on. APIs changing
    and approaches shifting slightly. As before, please feel free to try
    out but not stable yet. TJG
    
    **5th April 2016** Close to freeze for 1.0

NetworkZero makes it easier to use Python to connect things together 
across the. It's especially focused on the classroom 
or club situation where short-lived programs need to discover 
each other on the same or a different computer without having to 
know IP addresses or hostnames.

It offers two main services:

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
        nw0.send_message_to_address("Hello " + name)

[Machine or Process B and C and D ...]::

    import networkzero as nw0
    
    hello = nw0.discover("hello")
    nw0.send_message(hello, "World!")
    print(nw0.wait_for_message_from(hello))
    nw0.send_message(hello, "Tim")
    print(nw0.wait_for_message_from(hello))

This runs a service, advertised under the name "hello"
which will send back "Hello <name>" whenever <name> is sent to it.
Other machines or processes discover the service and send
names to it, receiving a greeting in return.

Read More
---------

.. toctree::
   :maxdepth: 3
   
   usage
   for-teachers
   for-students
   for-developers
