# -*- coding: utf-8 -*-
import logging
import random
import socket

def get_logger(name):
    #
    # For now, this is just a hand-off to logging.getLogger
    # Later, though, we might want to add a null handler etc.
    #
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger

_logger = get_logger(__name__)

#
# Common exceptions
#
class NetworkZeroError(Exception): 
    pass

class SocketAlreadyExistsError(NetworkZeroError): 
    pass

class SocketTimedOutError(NetworkZeroError): 
    pass

class InvalidAddressError(NetworkZeroError):
    pass

#
# Ports in the range 0xc000..0xffff are reserved
# for dynamic allocation
#
PORT_POOL = list(range(0xC000, 0X10000))

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
        random.shuffle(PORT_POOL)
        port = PORT_POOL.pop()
    
    try:
        addrinfo = socket.getaddrinfo(ip, port, socket.AF_INET)
    except socket.gaierror as exception:
        _logger.exception("Invalid Address %s", address)
        raise exc.InvalidAddressError("Invalid address: %s" % address)
    
    for addrinfo in addrinfo:
        return "%s:%s" % addrinfo[-1]
    else:
        raise exc.InvalidAddressError("Invalid address: %s" % address)
