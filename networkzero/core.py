# -*- coding: utf-8 -*-
import logging
import random
import socket

from . import config

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
PORT_POOL = list(config.DYNAMIC_PORTS)

def address(address=None):
    """Convert one of a number of inputs into a valid ip:port string.
    
    Elements which are not provided are filled in as follows:
    * IP Address: the system is asked for the set of IP addresses associated 
      with the machine and the first one is used.
    * Port number: a random port is selected from the pool of dynamically-available 
      port numbers.
      
    This means you can pass any of: nothing; an IP address; a port number; both
    
    If an IP address is supplied but is invalid from this machine, an InvalidAddressError
    exception is raised.
    
    :param address: (optional) Any of: an IP address, a port number, or both
    
    :returns: a valid ip:port string for this machine
    """
    address = str(address or "").strip()
    if ":" in address:
        ip, _, port = address.partition(":")
    else:   
        if address.isdigit():
            ip, port = "", address
        else:
            ip, port = address, ""
    
    if port and not port.isdigit():
        raise InvalidAddressError("Port %s must be a number" % port)
    
    if not port or not int(port):
        random.shuffle(PORT_POOL)
        port = PORT_POOL.pop()
    
    if not int(port) in config.VALID_PORTS:
        raise InvalidAddressError("Invalid port %s" % port)
    
    try:
        addrinfo = socket.getaddrinfo(ip, port, socket.AF_INET)
    except socket.gaierror as exception:
        _logger.exception("Invalid Address %s", address)
        raise InvalidAddressError("Invalid IP %s" % ip)
    
    for addrinfo in addrinfo:
        return "%s:%s" % addrinfo[-1]
    else:
        raise InvalidAddressError("Invalid address %s" % address)
