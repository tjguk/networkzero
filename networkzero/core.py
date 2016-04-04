# -*- coding: utf-8 -*-
import logging
import random
import re
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

def _setup_debug_logging():
    logger = logging.getLogger("networkzero")
    handler = logging.FileHandler("network.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

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

def split_address(address):
    if ":" in address:
        ip, _, port = address.partition(":")
    else:   
        if address.isdigit():
            ip, port = "", address
        else:
            ip, port = address, ""
    return ip, port

def is_valid_ip(ip):
    return bool(re.match("^\d{,3}\.\d{,3}\.\d{,3}\.\d{,3}$", ip))

def is_valid_port(port, port_range=range(65536)):
    try:
        return int(port) in port_range
    except ValueError:
        return False

def is_valid_address(address, port_range=range(65536)):
    ip, port = split_address(address)
    return is_valid_ip(ip) and is_valid_port(port, port_range)

def address(address=None):
    """Convert one of a number of inputs into a valid ip:port string.
    
    Elements which are not provided are filled in as follows:
        
        * IP Address: the system is asked for the set of IP addresses associated 
          with the machine and the first one is used.
        * Port number: a random port is selected from the pool of dynamically-available 
          port numbers.
      
    This means you can pass any of: nothing; an IP address; a port number; both
    
    If an IP address is supplied but is invalid, an InvalidAddressError
    exception is raised.
    
    :param address: (optional) Any of: an IP address, a port number, or both
    
    :returns: a valid ip:port string for this machine
    """
    address = str(address or "").strip()
    #
    # If the address is an ip:port pair, split into its component parts.
    # Otherwise, try to determine whether we're looking at an IP
    # or at a port and leave the other one blank
    #
    ip, port = split_address(address)
    
    #
    # If the port has been supplied, make sure it's numeric and that it's a valid
    # port number. If it hasn't been supplied, remove a random one from the pool
    # of possible dynamically-allocated ports and use that.
    #
    if port:
        try:
            port = int(port)
        except ValueError:
            raise InvalidAddressError("Port %s must be a number" % port)
        if port not in config.VALID_PORTS:
            raise InvalidAddressError("Port %d must be in range %d - %d" % (
                port, config.VALID_PORTS.start, config.VALID_PORTS.stop)
            )
    else:
        random.shuffle(PORT_POOL)
        port = PORT_POOL.pop()

    #
    # Attempt to valid the ip:port pair as a valid INET address.
    # If the IP address has not been supplied, this will return possible matches
    # from the list of IP addresses associated with this machine
    #
    try:
        addrinfo = socket.getaddrinfo(ip, port, socket.AF_INET)
    except socket.gaierror as exception:
        _logger.exception("Invalid Address %s", address)
        raise InvalidAddressError("Invalid IP %s" % ip)
    
    #
    # Pick an arbitrary one of the IP addresses matching the address
    #
    for addrinfo in addrinfo:
        return "%s:%s" % addrinfo[-1]
    else:
        raise InvalidAddressError("Invalid address %s" % address)
