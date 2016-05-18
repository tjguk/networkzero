# -*- coding: utf-8 -*-
"""Easy network discovery & messaging

Aimed at a classrom or club situation, networkzero makes it simpler to
have several machines or several processes on one machine discovering
each other and talking across a network. Typical examples would include:

* Sending commands to a robot
* Sending scores to a scoreboard
* Having a remote sensor ping a central controller
* A peer-to-peer chat / instant messenger

To send a message and wait for a reply::

    [Computer 1]
    import networkzero as nw0

    echo_address = nw0.advertise("echo")
    while True:
        name = nw0.wait_for_message_from(echo_address)
        nw0.send_reply_to(echo_address, "Hello " + name)

::

    [Computer 2]
    import networkzero as nw0

    echo_address = nw0.discover("echo")
    
    reply = nw0.send_message_to(echo_address, "Alice")
    print(reply)
    reply = nw0.send_message_to(echo_address, "Bob")
    print(reply)

To send news::

    [Computer 1]
    import networkzero as nw0
    
    address = nw0.advertise("data-logger")
    while True:
        #
        # ... do stuff
        #
        nw0.send_news_to(address, "data", ...)

::

    [Computer 2, 3, 4...]
    import networkzero as nw0
    
    logger = nw0.discover("data-logger")
    while True:
        topic, data = nw0.wait_for_news_from(logger, "data")
        #
        # ... write the data to a database etc.
        #

"""
from .core import (
    NetworkZeroError, SocketAlreadyExistsError, 
    SocketTimedOutError, InvalidAddressError,
    SocketInterruptedError, DifferentThreadError,
    
    address, action_and_params,
    string_to_bytes, bytes_to_string
)
from .discovery import advertise, discover, discover_all, discover_group
from .messenger import (
    send_message_to, wait_for_message_from, send_reply_to,
    send_news_to, wait_for_news_from
)
