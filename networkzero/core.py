# -*- coding: utf-8 -*-
import base64
import fnmatch
import logging
import random
import shlex
import socket

import netifaces

from . import config

def get_logger(name):
    #
    # For now, this is just a hand-off to logging.getLogger
    # Later, though, we might want to add a null handler etc.
    #
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger

_debug_logging_enabled = False
def _enable_debug_logging():
    global _debug_logging_enabled
    if not _debug_logging_enabled:
        logger = logging.getLogger("networkzero")
        handler = logging.FileHandler("network.log", "w", encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(threadName)s %(name)s %(levelname)s %(message)s"))
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        _debug_logging_enabled = True

_logger = get_logger(__name__)

#
# Common exceptions
#
class NetworkZeroError(Exception): 
    pass

class SocketAlreadyExistsError(NetworkZeroError): 
    pass

class SocketTimedOutError(NetworkZeroError):
    
    def __init__(self, n_seconds):
        self.n_seconds = n_seconds
    
    def __str__(self):
        return "Gave up waiting after %s seconds; this connection is now unusable" % self.n_seconds

class SocketInterruptedError(NetworkZeroError):
    
    def __init__(self, after_n_seconds):
        self.after_n_seconds = after_n_seconds
    
    def __str__(self):
        return "Interrupted after %s seconds; this connection is now unusable" % self.after_n_seconds

class AddressError(NetworkZeroError):
    pass

class NoAddressFoundError(AddressError):
    pass

class InvalidAddressError(NetworkZeroError):
    
    def __init__(self, address, errno=None):
        self.address = address
        self.errno = errno

    def __str__(self):
        message = "%s is not a valid address" % self.address
        if self.errno:
            message += "; the system returned an error of %d" % self.errno
        return message

class DifferentThreadError(NetworkZeroError):
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

def is_valid_ip_pattern(ip):
    """Check whether a string matches the outline of an IPv4 address, 
       allowing "*"  as a wildcard"""
    ip = ip.replace('*', '1')
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        # Not a valid IPv4 address pattern
        return False

def is_valid_port(port, port_range=range(65536)):
    try:
        return int(port) in port_range
    except ValueError:
        return False

def is_valid_address(address, port_range=range(65536)):
    ip, port = split_address(address)
    return is_valid_ip_pattern(ip) and is_valid_port(port, port_range)

_ip4_addresses = None
def _find_ip4_addresses():
    """Find all the IP4 addresses currently bound to interfaces
    """
    global _ip4_addresses
    if _ip4_addresses is None:
        _ip4_addresses = []
        for interface in netifaces.interfaces():
            for info in netifaces.ifaddresses(interface).get(netifaces.AF_INET, []):
                if info['addr']:
                    _ip4_addresses.append(info['addr'])

    # Make the default (first in list) IP be the one on the network with the
    # default gateway
    # Done here to avoid overriding current method of prioritising IP address
    # preferred by the user
    proto = socket.AF_INET
    default_gateway_interface = netifaces.gateways()['default'][proto][1]
    default_interface = netifaces.ifaddresses(default_gateway_interface)
    # Get first address on interface
    default_interface_address = default_interface[proto][0]['addr']
    _ip4_addresses.remove(default_interface_address)
    _ip4_addresses.insert(0, default_interface_address)

    return _ip4_addresses    

_ip4 = None
_prefer = None
def _find_ip4(prefer=None):
    global _ip4, _prefer
    #
    # Order the list of possible addresses on the machine: if any
    # address pattern is given as a preference (most -> least)
    # give it that weighting, otherwise treat all addresses
    # numerically. If no preference is given, prefer the most
    # likely useful local address range.
    #
    if prefer:
        _prefer = prefer
    else:
        _prefer = ["192.168.*"]
    def sorter(ip4):
        octets = [int(i) for i in ip4.split(".")]
        for n, pattern in enumerate(_prefer):
            if fnmatch.fnmatch(ip4, pattern):
                return n, octets
        else:
            #
            # Return the address itself if it doesn't match
            # a preference
            #
            return n + 1, octets
    
    ip4_addresses = _find_ip4_addresses()
    #
    # Pick an address allowing for user preference if stated
    #
    if not ip4_addresses:
        raise NoAddressFoundError
    else:
        #
        # Find the best match. If the user actually supplied a preference
        # list, assume an exact match is required to at least one of the
        # patterns.
        #
        ip4 = min(ip4_addresses, key=sorter)
        if prefer and not any(fnmatch.fnmatch(ip4, pattern) for pattern in prefer):
            raise NoAddressFoundError("No address matches any of: %s" % ", ".join(prefer))
        else:
            _ip4 = ip4
    
    return _ip4 

def address(address=None):
    """Convert one of a number of inputs into a valid ip:port string.
    
    Elements which are not provided are filled in as follows:
        
        * IP Address: the system is asked for the set of IP addresses associated 
          with the machine and the first one is used, preferring those matching
          `address` if it is a wildcard.
        * Port number: a random port is selected from the pool of dynamically-available 
          port numbers.
      
    This means you can pass any of: nothing; a hostname; an IP address; an IP address with wildcards; a port number
    
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
    host_or_ip, port = split_address(address)
    
    #
    # If the port has been supplied, make sure it's numeric and that it's a valid
    # port number. If it hasn't been supplied, remove a random one from the pool
    # of possible dynamically-allocated ports and use that.
    #
    if port:
        try:
            port = int(port)
        except ValueError:
            raise AddressError("Port %s must be a number" % port)
        if port not in config.VALID_PORTS:
            raise AddressError("Port %d must be in range %d - %d" % (
                port, min(config.VALID_PORTS), max(config.VALID_PORTS))
            )
    else:
        random.shuffle(PORT_POOL)
        port = PORT_POOL.pop()
    
    #
    # The address part could be an IP address (optionally including
    # wildcards to indicate a preference) or a hostname or nothing. 
    # If it's a hostname we attempt to resolve it to an IP address. 
    # It it's nothing or a wildcard we query the system for a matching IP address.
    #
    if (not host_or_ip) or is_valid_ip_pattern(host_or_ip):
        #
        # If a specific IP address is given, use that.
        # If an IP pattern is given (ie something with a wildcard in it) treat
        # that as no address with a preference for that wildcard.
        #
        prefer = None
        if "*" in host_or_ip:
            host_or_ip, prefer = None, [host_or_ip]
    
        #
        # If no IP (or only a wildcard) is specified, query the system for valid
        # addresses, preferring those which match the wildcard. NB if the preference
        # matches one we've previously used, we can return a cached address. But
        # different requests can specify different wildcard preferences.
        #
        if not host_or_ip:
            if _ip4 and _prefer == prefer:
                ip = _ip4
            else:
                ip = _find_ip4(prefer)
        else:
            ip = host_or_ip

    else:
        #
        # Treat the string as a hostname and resolve to an IP4 address
        #
        try:
            ip = socket.gethostbyname(host_or_ip)
        except socket.gaierror as exc:
            _logger.error("gaierror %d for %s", exc.errno, host_or_ip)
            raise InvalidAddressError(host_or_ip, exc.errno)
        else:
            #
            # Bizarrely specific check because BT Internet "helpfully"
            # redirects DNS fails to this address which hosts a sponsored
            # landing page!
            #
            if ip == "92.242.132.15":
                raise InvalidAddressError(host_or_ip, 0)
    
    return "%s:%s" % (ip, port)

def action_and_params(commandline):
    """Treat a command line as an action followed by parameter
    
    :param commandline: a string containing at least an action
    :returns: action, [param1, param2, ...]
    """
    components = shlex.split(commandline)
    return components[0], components[1:]

def bytes_to_string(data):
    """Take bytes and return a base64-encoded unicode string equivalent
    
    :param data: a bytes object
    :returns: base64-encoded unicode object
    """
    return base64.b64encode(data).decode("ascii")

def string_to_bytes(data):
    """Take a base64-encoded unicode string and return the equivalent bytes
    
    :param data: a base64-encoded unicode object
    :returns: the equivalent bytes
    """
    return base64.b64decode(data.encode("ascii"))
