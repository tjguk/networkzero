..  module:: networkzero

Usage
=====

Introduction
------------

At its core, NetworkZero offers two discovery functions and 7 message-sending functions:

Discovery
~~~~~~~~~

* :func:`advertise` -- advertise a named service running at an address
* :func:`discover` -- discover a service by name

Message-Sending
~~~~~~~~~~~~~~~

To send a message and receive a reply:

* :func:`send_message` -- send a message to an address
* :func:`wait_for_message` -- wait for a message to arrive at an address
* :func:`send_reply` -- send a reply from an address to a message

To send a command line which needs no reply (eg to instruct a robot):

* :func:`send_command` -- send a simple line of text to an address
* :func:`wait_for_command` -- wait for a command to arrive at an address and acknowledge it immediately

To have several machines subscribe to topics from a publisher:

* :func:`send_notification` -- send a message to everyone subscribed to a topic at an address
* :func:`wait_for_notification` -- subscribe to and wait for a topic-specific message from a publisher

Concepts
--------

NetworkZero is built around the idea of `addresses` and `messages`. 

Address
~~~~~~~

An `address` is a string containing an IP address and a port separated by a colon, 
exactly as you would type in to a web browser (except that you have to specify the port). 

Examples:

* `pi:1234`
* `127.0.0.1:45678`
* `192.168.0.5:9876`

If you know what you're about, you can simply pass one of these around directly, eg::

    import networkzero as nw0
    
    address = "127.0.0.1:1234"
    nw0.advertise("myservice", address)
    message = nw0.wait_for_message(address)
    
But to save you knowing what IP addresses and what ports are in use, NetworkZero 
makes it easy to generate an address automatically. If you pass no address to
:func:`advertise`, an address will be returned, constructed from your machine's 
IP address and a pool of spare ports.

..  note::

    You don't need to ask NetworkZero to generate an address: any valid address
    can be used. This can be useful in the unlikely event that the automatic address 
    is for the wrong network or clashes with an existing port.

Message
~~~~~~~

A message, for the message-passing and notification functionality, can be any built-in
Python object. This will often be just some text, but can be a number or a list, a tuple
or a dictionary. Note that the restriction to built-in objects is recursive: any lists
or dictionaries you send can themselves only contain built-in objects.

The command functions :func:`send_command` and :func:`wait_for_command` specifically
expect a simple string, such as you might type in on the command line.

Examples
~~~~~~~~

..  toctree::
    :maxdepth: 2
    :glob:
    
    cookbook/*
