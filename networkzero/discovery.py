# -*- coding: utf-8 -*-
import os, sys
import atexit
import collections
import csv
import io
import logging
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

def unpack(message):
    return marshal.loads(message)

def pack(message):
    return marshal.dumps(message)
    
class _Beacon(threading.Thread):
    
    rpc_port = 9998
    beacon_port = 9999
    finder_timeout_secs = 0.5
    beacon_message_size = 256
    interval_secs = config.BEACON_ADVERT_FREQUENCY_SECS
    
    def __init__(self):
        super().__init__(daemon=True)
        
        self._stop_event = threading.Event()
        self._services_to_advertise = {}
        self._services_found = {}
        self._lock = threading.Lock()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind(("", self.beacon_port))
        self.socket_fd = self.socket.fileno()
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        
        self.rpc = sockets.context.socket(zmq.REP)
        self.rpc.bind("tcp://*:%s" % self.rpc_port)

    def stop(self):
        _logger.debug("About to stop")
        self._stop_event.set()

    #
    # Commands available via RPC are methods whose
    # name starts with "do_"
    #
    def do_advertise(self, name, address):
        _logger.debug("Advertise %s on %s", name, address)
        
        with self._lock:
            address_found = self._services_to_advertise.get(name)
        
        if address_found:
            _logger.warn("Service %s already exists on %s", name, address_found)
            return None
        else:
            with self._lock:
                self._services_to_advertise[name] = core.address(address)
            return name
    
    def do_unadvertise(self, name, address):
        _logger.debug("Unadvertise %s on %s", name, address)
        
        with self._lock:
            address_found = self._services_to_advertise.get(name)
        
        if not address_found:
            _logger.warn("Not currently advertising %s on %s", name, address_found)
            return

        with self._lock:
            del self._services_to_advertise[name]
    
    def do_discover(self, name, wait_for_secs):
        _logger.debug("Discover %s waiting for %s secs", name, wait_for_secs)
        if wait_for_secs == -1:
            timeout_expired = lambda t: False
        else:
            t0 = time.time()
            timeout_expired = lambda t: t > t0 + wait_for_secs
                
        while not timeout_expired(time.time()):
            with self._lock:
                discovered = self._services_found.get(name)
            if discovered:
                return discovered
            else:
                time.sleep(0.1)
        else:
            _logger.warn("%s not discovered after %s secs", name, wait_for_secs)
            return None
    
    def do_discover_all(self):
        _logger.debug("Discover all")
        with self._lock:
            return list(self._services_found.items())
    
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
        segments = unpack(message)
        action, params = segments[0], segments[1:]
        function = getattr(self, "do_" + action.lower(), None)
        if not function:
            raise NotImplementedError
        else:
            _logger.debug("Calling %s with %s", function, params)
            result = function(*params)
            self.rpc.send(pack(result))
    
    def check_for_adverts(self):
        events = dict(self.poller.poll(1000 * self.finder_timeout_secs))
        if self.socket_fd not in events: 
            return

        message, source = self.socket.recvfrom(self.beacon_message_size)
        service_name, service_address = unpack(message)
        #~ _logger.debug("Advert received for %s on %s", service_name, service_address)
        with self._lock:
            self._services_found[service_name] = service_address

    def advertise_names(self):
        with self._lock:
            services = list(self._services_to_advertise.items())
        
        for service_name, service_address in services:
            #~ _logger.debug("Advertising %s on %s", service_name, service_address)
            message = pack([service_name, service_address])
            self.socket.sendto(message, 0, ("255.255.255.255", self.beacon_port))

    def run(self):
        _logger.info("Starting discovery")
        t0 = time.time()
        while not self._stop_event.wait(0):
            self.check_for_commands(wait=False)
            #
            # Advertise before checking for adverts
            # so that an advert called and checked within
            # the same cycle will be found
            #
            if time.time() > t0 + self.interval_secs:
                self.advertise_names()
                t0 = time.time()
            self.check_for_adverts()
        _logger.info("Ending discovery")
                
_beacon = None
_remote_beacon = object()

def start_beacon():
    global _beacon
    if _beacon is None:
        _logger.debug("About to start beacon")
        try:
            _beacon = _Beacon()
        except WindowsError as exc:
            if exc.errno == 10048:
                _beacon = _remote_beacon
            else:
                raise
        else:
            _beacon.start()

def _rpc(action, *args):
    with sockets.context.socket(zmq.REQ) as socket:
        socket.connect("tcp://localhost:%s" % _Beacon.rpc_port)
        socket.send(pack([action] + list(args)))
        return unpack(socket.recv())

def advertise(name, address=None):
    start_beacon()
    address = core.address(address)
    _rpc("advertise", name, address)
    atexit.register(unadvertise, name, address)
    return address

def unadvertise(name, address):
    start_beacon()
    return _rpc("unadvertise", name, core.address(address))
    
def discover(name, wait_for_secs=60):
    start_beacon()
    return _rpc("discover", name, wait_for_secs)

def discover_all():
    start_beacon()
    return _rpc("discover_all")

if __name__ == '__main__':
    pass
