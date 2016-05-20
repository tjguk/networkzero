NetworkZero
===========

.. image:: https://travis-ci.org/tjguk/networkzero.svg?branch=master
    :target: https://travis-ci.org/tjguk/networkzero

Make it easy for learning groups to use simple networking in Python

* Docs: http://networkzero.readthedocs.org/en/latest/

* Development: https://github.com/tjguk/networkzero

* Tests: to run the tests, run tox. All tests are run on Travis (Linux & Apple)
  and Appveyor (Windows)

API
---

address below refers to an IP:Port string eg "192.0.2.5:4567"

Discovery
~~~~~~~~~

* address = advertise(name, address=None)

* address = discover(name, wait_for_s=FOREVER)

* [(name, address), ...] = discover_all()

* [(name, address), ...] = discover_group(group_name, separator="/")

Messaging
~~~~~~~~~

* reply = send_message_to(address, message, wait_for_reply_s=FOREVER)

* message = wait_for_message_from(address, [wait_for_s=FOREVER])

* send_reply_to(address, reply)

* send_news_to(address, news)

* wait_for_news_from(address[, pattern=EVERYTHING][, wait_for_s=FOREVER])

Typical Usage
-------------

On computer (or process) A:

.. code-block:: python

    import networkzero as nw0
    
    address = nw0.advertise("hello")
    while True:
        name = nw0.wait_for_message_from(address)
        nw0.send_reply_to(address, "Hello, %s" % name)
        
On computer (or process) B and C and D...:

.. code-block:: python

    import networkzero as nw0
    
    server = nw0.discover("hello")
    reply = nw0.send_message_to(server, "World")
    print(reply)
    reply = nw0.send_message_to(server, "Tim")
    print(reply)
