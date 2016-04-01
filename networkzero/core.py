# -*- coding: utf-8 -*-
import socket

from . import exc
from .logging import logger

#
# Ports in the range 0xc000..0xffff are reserved
# for dynamic allocation
#
PORT_POOL = set(range(0xC000, 0X10000))

def address(address=None):
    """Take one of a number if things which can be treated as a nw0
    address and return a valid IP:Port string.
    """
    address = str(address or "").strip()
    if ":" in address:
        ip, _, port = address.partition(":")
    else:
        if address.isdigit():
            ip, port = "", address
        else:
            ip, port = address, ""
    if not port or not int(port):
        port = PORT_POOL.pop()
    
    #
    # An ip of None will return 127.0.0.1; an ip of "" will return the first
    # IP address from socket.gethostbyname_ex("")
    #
    try:
        addrinfo = socket.getaddrinfo(ip, port, socket.AF_INET)
    except socket.gaierror as exception:
        logger.exception("Invalid Address %s", address)
        raise exc.InvalidAddressError("Invalid address: %s" % address)
    
    for addrinfo in addrinfo:
        return "%s:%s" % addrinfo[-1]
    else:
        raise exc.InvalidAddressError("Invalid address: %s" % address)
