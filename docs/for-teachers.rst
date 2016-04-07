For Teachers
============

Introduction
------------

Have you ever wanted to get one computer to talk to another with the
minimum of fuss? Perhaps to have a laptop talk to a robot? Or just to
get the "wow!" factor of a chat or a photo go from one machine to another.
Or to extend a simple game into two-player mode with each player on a
different computer? Or to have a RPi with a temperature sensor send its
readings to a workstation showing graphs?

To do that, you need two key things: to know the names or addresses of
each computer in the scheme; and to have each one listen and respond
to messages from the other.

NetworkZero makes that possible and even easy from within Python, running
on any supported platform, including Windows, Mac and Linux boxes such as
the Raspberry Pi.

Benefits
--------

The benefits of NetworkZero fall into two categories: the advantages which
communicating over a network bring; and, given that you are using a network,
the benefits of using NetworkZero.

Using a Network
~~~~~~~~~~~~~~~

*   Network-based programs are more loosely coupled. This is generally considered
    A Good Thing.
    
*   A set of programs communicating across a network are usually agnostic as to
    platform and language. You could have a headless RaspberryPi with a sensor
    attached sending data to a Windows PC with a graphical output.

Using NetworkZero
~~~~~~~~~~~~~~~~~

*   NetworkZero makes it easier to advertise and discover services running on the
    network on the same or different machines. However, the discovery is always
    merely a shortcut: it's always possible to pass a literal ip:port address.

*   Three simple means of sending and receiving data, each with its own
    semantics and uses.

*   Simple Python data can be sent transparently. Except when sending/receiving
    commands, the messages passed can be any built-in Python object. This obviously
    includes strings and numbers, but also includes tuples, lists & dictionaries.


Difficulties
------------

Even with the advantages which NetworkZero brings, there are still some difficulties:

Messy Network Setups
~~~~~~~~~~~~~~~~~~~~

NetworkZero assumes a fairly simple setup on each of the machines and the network
in general. For a classroom of networked RPis or laptops, this is likely to be the
case. But, if you have an inventive network manager, you may find that the laptops
and the RPi boxes are on two separate subnets or VLANs and that the broadcast mechanism
which allows for discovery doesn't work.

Or it might be that one or more machines have multiple IP addresses. This could be the
case, for example, if you have a PiNet setup running over wired ethernet while the boxes
also have WiFi adapters. This might mean that the address which one advertises is on its
ethernet address while the other attempts to reach it over WiFi.

Keyboard Input blocks the network
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Imagine you're writing a simple chat program where you want the students
to see updates come in from the others while typing their own messages.
The trouble is that the normal means of waiting for keyboard input (the 
`input` function) blocks all other activity: the incoming messages will
simply queue up until the user presses `Enter`.

The chat program in the examples/ folder avoids this by having the keyboard
input in one program with the updates showing in another. Both windows are
running on the student's machine and coordinating via the network.

There *are* techniques for looking for keyboard input without blocking. But
none is cleanly cross-platform and really needs a separate package (KeyboardZero?).
Of course, using a different interface such as PyGame or of the GUI packages
available for Python would avoid this. But each brings its own complexity.

Thinking in Network
~~~~~~~~~~~~~~~~~~~

Perhaps the most important roadblock is that you have, in some cases, to change
your way of thinking about a program when you're coordinating across a network.
NetworkZero smoothes away some of the complexity, but it's ultimately a good
idea for students to understand how network-based programs differ from local ones.

Some of the factors are:

* Message passing vs shared variables
* Event-driven activity, reacting to incoming data
* Possible loss of remote nodes
* Dealing with blocking/non-blocking I/O
