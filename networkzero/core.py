# -*- coding: utf-8 -*-
import socket

import zmq
context = zmq.Context()

from . import exc

def address(address):
    """Take one of a number if things which can be treated as a nw0
    address and return a valid IP:Port string.
    """
    address = str(address).strip()
    if ":" in address:
        ip, _, port = address.partition(":")
    else:
        ip, port = "", address
    if ip == "*":
        ip = "0.0.0.0"
    
    for addrinfo in socket.getaddrinfo(ip, port, socket.AF_INET):
        return "%s:%s" % addrinfo[-1]
    else:
        raise exc.InvalidAddressError("Invalid address: %s" % (address))
