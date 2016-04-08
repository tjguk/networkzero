# -*- coding: utf-8 -*-
"""Advertise and collect advertisements of network services

The discovery module offers:

* A UDP broadcast socket which:
  - Listens for and keeps track of service adverts from this and other 
    machines & processes
  - Broadcasts services advertised by this process

* A ZeroMQ socket which allow any process on this machine to 
  communicate with its broadcast socket

The beacon is started automatically in a daemon thread when the first 
attempt is made to advertise or discover. If another process already 
has a beacon running (ie if this beacon can't bind to its port) this 
beacon thread will shut down with no further action.

The module-level functions to advertise and discover will open a connection
to a ZeroMQ socket on this machine (which might be hosted by this or by another
process) and will use this socket to send commands to the beacon thread which
will update or return its internal list of advertised services.

As an additional convenience, the :func:`advertise` function will, if given no
specific address, generate a suitable ip:port pair by interrogating the system.
This functionality is actually in :func:`core.address` (qv).
"""
import os, sys
import atexit
import collections
import csv
import io
import marshal
import random
import socket
import threading
import time

import zmq

from . import config
from . import core
from . import sockets

_logger = core.get_logger(__name__)

def _unpack(message):
    return marshal.loads(message)

def _pack(message):
    return marshal.dumps(message)
    
def bind_with_timeout(function, args, n_tries=3, retry_interval_s=0.5):
    n_tries_left = n_tries
    while n_tries_left > 0:
        try:
            return function(*args)
        except zmq.error.ZMQError as exc:
            _logger.warn("%s; %d tries remaining", exc, n_tries_left)
            n_tries_left -= 1
        
class _Beacon(threading.Thread):
    
    rpc_port = 9998
    beacon_port = 9999
    finder_timeout_s = 0.5
    beacon_message_size = 256
    interval_s = config.BEACON_ADVERT_FREQUENCY_S
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._stop_event = threading.Event()
        
        #
        # Because incoming broadcasts and requests for discovery can arrive
        # asynchronously, we need to ensure only one reader/writer at a time
        #
        self._lock = threading.Lock()
        
        #
        # Services we're advertising
        #
        self._services_to_advertise = {}
        #
        # Broadcast adverts which we've received (some of which will be our own)
        #
        self._services_found = {}
        
        #
        # Set the socket up to broadcast datagrams over UDP
        #
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #
        # On Unix, restarting the beacon on a fixed port only a short time after closing
        # it will often fail because the socket is still in a TIME_WAIT state. If we
        # set the SO_REUSEADDR option before binding, we'll override that check at the
        # small risk of picking up some stray packets undelivered to the socket's
        # previous incarnation.
        #
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bind_with_timeout(self.socket.bind, (("", self.beacon_port),))
        #
        # Add the raw UDP socket to a ZeroMQ socket poller so we can check whether
        # it's received anything as part of the beacon's main event loop.
        #
        self.socket_fd = self.socket.fileno()
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        
        self.rpc = sockets.context.socket(zmq.REP)
        #
        # To avoid problems when restarting a beacon not long after it's been
        # closed, force the socket to shut down regardless about 1 second after 
        # it's been closed.
        #
        self.rpc.linger = 0
        bind_with_timeout(self.rpc.bind, ("tcp://127.0.0.1:%s" % self.rpc_port,))

    def stop(self):
        _logger.debug("About to stop")
        self._stop_event.set()

    #
    # Commands available via RPC are methods whose name starts with "do_"
    #
    def do_advertise(self, name, address, fail_if_exists):
        _logger.debug("Advertise %s on %s %s", name, address, fail_if_exists)
        canonical_address = core.address(address)
        
        with self._lock:
            address_found = self._services_to_advertise.get(name)
        
        if address_found:
            if fail_if_exists:
                _logger.error("Service %s already exists on %s", name, address_found)
                return None
            else:
                _logger.warn("Superseding service %s which already exists on %s", name, address_found)

        with self._lock:
            self._services_to_advertise[name] = canonical_address
            #
            # As a shortcut, automatically "discover" any services we ourselves are advertising
            #
            self._services_found[name] = canonical_address
            
        return canonical_address
    
    def do_discover(self, name, wait_for_s):
        _logger.debug("Discover %s waiting for %s seconds", name, wait_for_s)
        if wait_for_s == -1:
            timeout_expired = lambda t: False
        else:
            t0 = time.time()
            timeout_expired = lambda t: t > t0 + wait_for_s
                
        while True:
            with self._lock:
                discovered = self._services_found.get(name)
            if discovered:
                return discovered
            if timeout_expired(time.time()):
                break
            else:
                time.sleep(0.1)
        else:
            _logger.warn("%s not discovered after %s seconds", name, wait_for_s)
            return None
    
    def do_discover_all(self):
        _logger.debug("Discover all")
        with self._lock:
            return list(self._services_found.items())
    
    def do_stop(self):
        _logger.debug("Stop")
        self.stop()
    
    #
    # Main loop:
    # * Check for incoming RPC commands
    # * Check for broadcast adverts
    # * Broadcast any adverts of our own
    #
    def check_for_commands(self, wait=True):
        """The rpc socket will receive a utf-8, json-encoded command
        with 1 or more segments. The first is always an action; any others
        are the parameters.
        
        The actions result in methods being called on this instance; the result
        of a method is re-encoded as json and passed back to the socket.
        """
        try:
            message = self.rpc.recv(0 if wait else zmq.NOBLOCK)
        except zmq.ZMQError as exc:
            if exc.errno == zmq.EAGAIN:
                return
            else:
                raise
        
        _logger.debug("Received command %s", message)
        segments = _unpack(message)
        action, params = segments[0], segments[1:]
        function = getattr(self, "do_" + action.lower(), None)
        if not function:
            raise NotImplementedError
        else:
            _logger.debug("Calling %s with %s", action, params)
            try:
                result = function(*params)
            except:
                _logger.exception("Problem calling %s with %s", action, params)
                result = None
            self.rpc.send(_pack(result))
    
    def check_for_adverts(self):
        events = dict(self.poller.poll(1000 * self.finder_timeout_s))
        if self.socket_fd not in events: 
            return

        message, source = self.socket.recvfrom(self.beacon_message_size)
        service_name, service_address = _unpack(message)
        with self._lock:
            self._services_found[service_name] = service_address

    def advertise_names(self):
        with self._lock:
            services = list(self._services_to_advertise.items())
        
        for service_name, service_address in services:
            message = _pack([service_name, service_address])
            self.socket.sendto(message, 0, ("255.255.255.255", self.beacon_port))

    def run(self):
        _logger.info("Starting discovery")
        t0 = time.time()
        while not self._stop_event.wait(0):
            
            #
            # Check for instruction to advertise/discover from a
            # local process (this or another on this machine)
            #
            self.check_for_commands(wait=False)
            
            #
            # If we've reached the interval tick for advertising,
            # advertise all the names registered.
            #
            if time.time() > t0 + self.interval_s:
                self.advertise_names()
                t0 = time.time()
            
            #
            # See if any advert broadcasts have arrived
            #
            self.check_for_adverts()
        
        _logger.info("Ending discovery")

_beacon = None
_remote_beacon = object()

def _start_beacon():
    """Start a beacon thread within this process if no beacon is currently
    running on this machine.
    
    In general this is called automatically when an attempt is made to
    advertise or discover. It might be convenient, though, to call this
    function directly if you want to have a process whose only job is
    to host this beacon so that it doesn't shut down when other processes
    shut down.
    """
    global _beacon
    if _beacon is None:
        _logger.debug("About to start beacon")
        try:
            _beacon = _Beacon()
        except OSError as exc:
            if exc.errno == 10048:
                _logger.warn("Beacon already active on this machine")
                #
                # _remote_beacon is simply a not-None sentinel value
                # to distinguish between the case where we have not
                # yet started a beacon and where we have found one
                # in another process.
                #
                _beacon = _remote_beacon
            else:
                raise
        else:
            _beacon.start()

def _rpc(action, *args):
    _logger.debug("About to send rpc request %s with args %s", action, args)
    with sockets.context.socket(zmq.REQ) as socket:
        #
        # To avoid problems when restarting a beacon not long after it's been
        # closed, force the socket to shut down regardless about 1 second after 
        # it's been closed.
        #
        socket.linger = 0
        socket.connect("tcp://localhost:%s" % _Beacon.rpc_port)
        socket.send(_pack([action] + list(args)))
        return _unpack(socket.recv())

def advertise(name, address=None, fail_if_exists=False):
    """Advertise a name at an address
    
    Start to advertise service `name` at address `address`. If
    the address is not supplied, one is constructed and this is
    returned by the function. ie this is a typical use::
    
        address = nw0.advertise("myservice")
        
    :param name: any text
    :param address: either "ip:port" or None
    :param fail_if_exists: fail if this name is already registered?
    :returns: the address given or constructed
    """
    _start_beacon()
    return _rpc("advertise", name, address, fail_if_exists)
    return address

def discover(name, wait_for_s=60):
    """Discover a service by name
    
    Look for an advert to a named service::
    
        address = nw0.discover("myservice")
        
    :param name: any text
    :param wait_for_s: how many seconds to wait before giving up
    :returns: the address found or None
    """
    _start_beacon()
    return _rpc("discover", name, wait_for_s)

def discover_all():
    """Produce a list of all known services and their addresses
    
    Ask for all known services as a list of 2-tuples: (name, address)
    This could, eg, be used to form a dictionary of services::
    
        services = dict(nw0.discover_all())
        
    :returns: a list of 2-tuples [(name, address), ...]
    """
    _start_beacon()
    return _rpc("discover_all")

def stop_beacon():
    """Stop the beacon, typically to solve a problem with stale names.
    
    You do not normally need to call this: do not use this unless you 
    know what you are about. 
    """
    global _beacon
    _start_beacon()
    _rpc("stop")
    _beacon.join()
    _beacon = None

if __name__ == '__main__':
    pass
