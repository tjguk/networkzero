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
        name = nw0.wait_for_message(echo_address)
        nw0.send_reply(echo_address, "Hello " + name)

    [Computer 2]
    import networkzero as nw0

    echo_address = nw0.discover("echo")
    print(nw0.send_message(echo_address, "Alice"))
    print(nw0.send_message(echo_address, "Bob"))


To send a command without waiting for a reply::

    [Computer 1]
    import networkzero as nw0
    
    address = nw0.advertise("robot")
    while True:
        command, params = nw0.wait_for_command(address)
        if command == "FORWARD": 
            # ...
        elif command == "TURN":
            [direction, degrees] = params
            # ...
        

    [Computer 2]
    import networkzero as nw0

    robot = nw0.discover("robot")
    nw0.send_command("FORWARD")
    nw0.send_command("TURN LEFT 45")

To send notifications::

    [Computer 1]
    import networkzero as nw0
    
    address = nw0.advertise("data-logger")
    while True:
        #
        # ... do stuff
        #
        nw0.send_notification(address, "data", ...)

    [Computer 2, 3, 4...]
    import networkzero as nw0
    
    logger = nw0.discover("data-logger")
    while True:
        topic, data = nw0.wait_for_notification(address, topic)
        #
        # ... write the data to a database etc.
        #

"""
from .core import (
    NetworkZeroError, SocketAlreadyExistsError, 
    SocketTimedOutError, InvalidAddressError,
    SocketInterruptedError,
    address, split_command
)
from .discovery import advertise, discover, discover_all
from .messenger import (
    send_command, wait_for_command, 
    send_message, wait_for_message, send_reply, 
    send_notification, wait_for_notification
)
