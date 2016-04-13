NetworkZero
===========

.. image:: https://travis-ci.org/tjguk/networkzero.svg?branch=master
    :target: https://travis-ci.org/tjguk/networkzero

Make it easy for learning groups to use simple networking in Python

..  note::

    **10th April 2016** This is under heavy development at the moment; things
    can and will change, possibly quite radically, over the next few days 
    and weeks. Please do take it for a spin, but don't base any long-term
    plans on the current API. TJG

* Docs: http://networkzero.readthedocs.org/en/latest/

* Development: https://github.com/tjguk/networkzero

At the time of writing, all 27 tests pass on:

* Windows 8
* Debian Jessie
* Raspbian Jessie
* Mac OS/X 10.11

* Tests: to run the tests, run tox

API
---

address below refers to an IP:Port string eg "192.168.1.5:4567"

Discovery
~~~~~~~~~

* address = advertise(name, address=None)

* address = discover(name, wait_for_secs=FOREVER)

* unadvertise(name[, wait_for_secs=SHORT_WAIT])

* [(name, address), ...] = discover_all()

Messaging
~~~~~~~~~

* send_message(address, question[, wait_for_response_secs=FOREVER])

* message = wait_for_message(address, [wait_for_secs=FOREVER])

* send_reply(address, reply)

* send_notification(address, notification)

* wait_for_notification(address[, pattern=EVERYTHING][, wait_for_secs=FOREVER])

Typical Usage
-------------

On computer (or process) A::

    import networkzero as nw0
    
    address = nw0.advertise("hello")
    while True:
        name = nw0.wait_for_message(address)
        nw0.send_reply(address, "Hello, %s" % name)
        
On computer (or process) B and C and D...::

    import networkzero as nw0
    
    hello = nw0.discover("hello")
    reply = nw0.send_message(hello, "World")
    print(reply)
    reply = nw0.send_message(hello, "Tim")
    print(reply)

