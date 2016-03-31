# -*- coding: utf-8 -*-
import socket
import urllib.parse

import zmq
context = zmq.Context()

from . import exc
from .logging import logger

def address(address=None):
    """Take one of a number if things which can be treated as a nw0
    address and return a valid IP:Port string.
    """
    if address is None:
        address = ""
    address = str(address).strip()
    if ":" in address:
        ip, _, port = address.partition(":")
    else:
        if address.isdigit():
            ip, port = "", address
        else:
            ip, port = address, ""
    if ip == "*":
        ip = "0.0.0.0"
    
    #
    # An ip of None will return 127.0.0.1; an ip of "" will return the first
    # IP address from socket.gethostbyname_ex("")
    #
    try:
        addrinfo = socket.getaddrinfo(ip, port, socket.AF_INET)
    except socket.gaierror as exc:
        logger.exception("Invalid Address %s", address)
        raise exc.InvalidAddressError("Invalid address: %s" % address)
    
    for addrinfo in addrinfo:
        return "%s:%s" % addrinfo[-1]
    else:
        raise exc.InvalidAddressError("Invalid address: %s" % address)

def socket_address(socket):
    return urllib.parse.parse(socket.last_endpoint).netloc
