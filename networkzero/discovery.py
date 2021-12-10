# -*- coding: utf-8 -*-
"""Advertise and collect advertisements of network services

The discovery module offers:

    * A UDP broadcast socket which:

      - Listens for and keeps track of service adverts from this and other
        machines & processes
      - Broadcasts services advertised by this process

    * A ZeroMQ socket which allow any process on this machine to
      communicate with its broadcast socket

In other words, we have a beacon which listens to instructions
from processes on this machine while sending out and listening
to adverts broadcast to/from all machines on the network.

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
This functionality is actually in :func:`networkzero.address` (qv).
"""
from __future__ import print_function
import os, sys
import atexit
import collections
import errno
import json
import logging
import socket
import threading
import time

import zmq

from . import config
from . import core
from . import sockets

_logger = core.get_logger(__name__)

#
# Continue is a sentinel value to indicate that a command
# has completed its scheduled slice without producing a result
# and without exceeding its overall timeout.
#
Continue = object()

#
# Empty is a sentinel to distinguish between no result and a result of None
#
Empty = object()

def _unpack(message):
    return json.loads(message.decode(config.ENCODING))

def _pack(message):
    return json.dumps(message).encode(config.ENCODING)

def timed_out(started_at, wait_for_s):
    #
    # If the wait time is the sentinel value FOREVER, never time out
    # Otherwise time out if the current time is more than wait_for_s seconds after the start time
    #
    if wait_for_s is config.FOREVER:
        return False
    else:
        return time.time() > started_at + wait_for_s

def _bind_with_timeout(bind_function, args, n_tries=3, retry_interval_s=0.5):
    """Attempt to bind a socket a number of times with a short interval in between

    Especially on Linux, crashing out of a networkzero process can leave the sockets
    lingering and unable to re-bind on startup. We give it a few goes here to see if
    we can bind within a couple of seconds.
    """
    n_tries_left = n_tries
    while n_tries_left > 0:
        try:
            return bind_function(*args)
        except zmq.error.ZMQError as exc:
            _logger.warn("%s; %d tries remaining", exc, n_tries_left)
            n_tries_left -= 1
        except OSError as exc:
            if exc.errno == errno.EADDRINUSE:
                _logger.warn("%s; %d tries remaining", exc, n_tries_left)
                n_tries_left -= 1
            else:
                raise
    else:
        raise core.SocketAlreadyExistsError("Failed to bind after %s tries" % n_tries)

class _Service(object):
    """Convenience container with details of a service to be advertised

    Includes the name, address and when it is next due to be advertised
    and when it is due to expire if it was discovered.
    """

    def __init__(self, name, address, ttl_s=None):
        self.name = name
        self.address = address
        self.ttl_s = ttl_s
        self.expires_at = None if ttl_s is None else (time.time() + ttl_s)
        self.advertise_at = 0

    def __str__(self):
        return "_Service %s at %s due to advertise at %s and expire at %s" % (
            self.name, self.address,
            time.ctime(self.advertise_at), time.ctime(self.expires_at)
        )

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, str(self))

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

class _Command(object):
    """Convenience container with details of a running command

    Includes the action ("discover", "advertise" etc.), its parameters, when
    it was started -- for timeout purposes -- and any response.

    This is used by the process_command functionality
    """

    def __init__(self, action, params):
        self.action = action
        self.params = params
        self.started_at = time.time()
        self.response = Empty

    def __str__(self):
        return "_Command: %s (%s) started at %s -> %s" % (self.action, self.params, time.ctime(self.started_at), self.response)

class _Beacon(threading.Thread):
    """Threaded beacon to: listen for adverts & broadcast adverts
    """

    rpc_port = 9998
    beacon_port = 9999
    finder_timeout_s = 0.05
    beacon_message_size = 256
    time_between_broadcasts_s = config.BEACON_ADVERT_FREQUENCY_S

    def __init__(self, beacon_port=None):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._stop_event = threading.Event()
        self._is_paused = False

        self.beacon_port = beacon_port or self.__class__.beacon_port
        _logger.debug("Using beacon port %s", self.beacon_port)

        #
        # Services we're advertising
        #
        self._services_to_advertise = collections.deque()
        #
        # Broadcast adverts which we've received (some of which will be our own)
        #
        self._services_found = {}

        #
        # _Command requests are collected on one queue
        # _Command responses are added to another
        #
        self._command = None

        #
        # Set the socket up to broadcast datagrams over UDP
        #
        self.broadcast_addresses = set(core._find_ip4_broadcast_addresses())
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind(("", self.beacon_port))
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
        self.rpc.linger = 1000
        _bind_with_timeout(self.rpc.bind, ("tcp://127.0.0.1:%s" % self.rpc_port,))

    def stop(self):
        _logger.debug("About to stop")
        self._stop_event.set()

    #
    # Commands available via RPC are methods whose name starts with "do_"
    #
    def do_advertise(self, started_at, name, address, fail_if_exists, ttl_s):
        _logger.debug("Advertise %s on %s %s TTL=%s", name, address, fail_if_exists, ttl_s)
        canonical_address = core.address(address)

        superseded_services = set()
        for service in self._services_to_advertise:
            if service.name == name:
                if fail_if_exists:
                    _logger.error("_Service %s already exists on %s", name, service.address)
                    return None
                else:
                    _logger.warn("Superseding service %s which already exists on %s", name, service.address)
                    superseded_services.add(service)

        for s in superseded_services:
            self._services_to_advertise.remove(s)

        service = _Service(name, canonical_address, ttl_s)
        self._services_to_advertise.append(service)
        #
        # As a shortcut, automatically "discover" any services we ourselves are advertising
        #
        self._services_found[name] = service

        return canonical_address

    def do_unadvertise(self, started_at, name):
        _logger.debug("Unadvertise %s", name)
        for service in self._services_to_advertise:
            if service.name == name:
                self._services_to_advertise.remove(service)
                break
        else:
            _logger.warn("No advert found for %s", name)
        _logger.debug("Services now: %s", self._services_to_advertise)

    def do_pause(self, started_at):
        _logger.debug("Pause")
        self._is_paused = True

    def do_resume(self, started_at):
        _logger.debug("Resume")
        self._is_paused = False

    def do_discover(self, started_at, name, wait_for_s):
        _logger.debug("Discover %s waiting for %s seconds", name, wait_for_s)

        discovered = self._services_found.get(name)

        #
        # If we've got a match, return it. Otherwise:
        # * If we're due to wait for ever, continue
        # * If we're out of time return None
        # * Otherwise we've still got time left: continue
        #
        if discovered:
            return discovered.address

        if timed_out(started_at, wait_for_s):
            return None
        else:
            return Continue

    def do_discover_all(self, started_at):
        _logger.debug("Discover all")
        return [(service.name, service.address) for service in self._services_found.values()]

    def do_reset(self, started_at):
        _logger.debug("Reset")
        self.do_pause(started_at)
        self._services_found.clear()
        self._services_to_advertise.clear()
        self.do_resume(started_at)

    def do_stop(self, started_at):
        _logger.debug("Stop")
        self.stop()

    def listen_for_one_advert(self):
        events = dict(self.poller.poll(1000 * self.finder_timeout_s))
        if self.socket_fd not in events:
            return

        message, source = self.socket.recvfrom(self.beacon_message_size)
        _logger.debug("Broadcast message received: %r", message)
        service_name, service_address, ttl_s = _unpack(message)
        service = _Service(service_name, service_address, ttl_s)
        self._services_found[service_name] = service

    def broadcast_one_advert(self):
        if self._services_to_advertise:
            next_service = self._services_to_advertise[0]
            if next_service.advertise_at < time.time():
                _logger.debug("%s due to advertise at %s", next_service.name, time.ctime(next_service.advertise_at))
                message = _pack([next_service.name, next_service.address, next_service.ttl_s])
                for broadcast_address in self.broadcast_addresses:
                    _logger.debug("Advertising on %s", broadcast_address)
                    self.socket.sendto(message, 0, (broadcast_address, self.beacon_port))
                next_service.advertise_at = time.time() + self.time_between_broadcasts_s
                self._services_to_advertise.rotate(-1)

    def remove_expired_adverts(self):
        for name, service in list(self._services_found.items()):
            #
            # A service with an empty expiry time never expires
            #
            if service.expires_at is None:
                continue
            if service.expires_at <= time.time():
                _logger.warn("Removing advert for %s which expired at %s",
                    name, time.ctime(service.expires_at))
                del self._services_found[name]

    def poll_command_request(self):
        """If the command RPC socket has an incoming request,
        separate it into its action and its params and put it
        on the command request queue.
        """
        try:
            message = self.rpc.recv(zmq.NOBLOCK)
        except zmq.ZMQError as exc:
            if exc.errno == zmq.EAGAIN:
                return
            else:
                raise

        _logger.debug("Received command %s", message)
        segments = _unpack(message)
        action, params = segments[0], segments[1:]
        _logger.debug("Adding %s, %s to the request queue", action, params)
        self._command = _Command(action, params)

    def process_command(self):
        if not self._command:
            return
        else:
            _logger.debug("process_command: %s", self._command.action)
            command = self._command

        _logger.debug("Picked %s, %s, %s", self._command.action, self._command.params, self._command.started_at)
        function = getattr(self, "do_" + command.action.lower(), None)
        if not function:
            raise NotImplementedError("%s is not a valid action")
        else:
            try:
                result = function(command.started_at, *command.params)
            except:
                _logger.exception("Problem calling %s with %s", command.action, command.params)
                result = None

            _logger.debug("result = %s", result)

            #
            # result will be Continue if the action cannot be completed
            # (eg a discovery) but its time is not yet expired. Leave
            # the command on the stack for now.
            #
            if result is Continue:
                return

            #
            # If we get a result, add the result to the response
            # queue and pop the request off the stack.
            #
            self._command.response = result

    def poll_command_reponse(self):
        """If the latest request has a response, issue it as a
        reply to the RPC socket.
        """
        if self._command.response is not Empty:
            _logger.debug("Sending response %s", self._command.response)
            self.rpc.send(_pack(self._command.response))
            self._command = None

    def run(self):
        _logger.info("Starting discovery")
        while not self._stop_event.wait(0):

            try:
                #
                # If we're not already processing one, check for an command
                # to advertise/discover from a local process.
                #
                if not self._command:
                    self.poll_command_request()

                #
                # If we're paused no adverts will be broadcast. Adverts
                # will be received and stale ones expired
                #
                if not self._is_paused:
                    #
                    # Broadcast the first advert whose advertising schedule
                    # has arrived
                    #
                    self.broadcast_one_advert()

                #
                # See if an advert broadcast has arrived
                #
                self.listen_for_one_advert()

                #
                # See if any adverts have expired
                #
                self.remove_expired_adverts()

                #
                # If we're processing a command, see if it's complete
                #
                if self._command:
                    self.process_command()
                    self.poll_command_reponse()

            except:
                _logger.exception("Problem in beacon thread")
                break

        _logger.info("Ending discovery")
        self.rpc.close()
        self.socket.close()

_beacon = None
_remote_beacon = object()

def _start_beacon(port=None):
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
        _logger.debug("About to start beacon with port %s", port)
        try:
            _beacon = _Beacon(port)
        except (OSError, socket.error) as exc:
            if exc.errno == errno.EADDRINUSE:
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

def _stop_beacon():
    #
    # Mostly for testing: shutdown the beacon if it's running
    # locally and clear it globally so the next attempt will
    # start fresh.
    #
    global _beacon
    if _beacon and _beacon is not _remote_beacon:
        _beacon.stop()
        _beacon.join()
    _beacon = None

def _rpc(action, *args, **kwargs):
    _logger.debug("About to send rpc request %s with args %s, kwargs %s", action, args, kwargs)
    wait_for_s = kwargs.pop("wait_for_s", 5)
    with sockets.context.socket(zmq.REQ) as socket:
        #
        # To avoid problems when restarting a beacon not long after it's been
        # closed, force the socket to shut down regardless about 1 second after
        # it's been closed.
        #
        socket.connect("tcp://localhost:%s" % _Beacon.rpc_port)
        socket.send(_pack([action] + list(args)))
        reply = sockets._sockets._receive_with_timeout(socket, wait_for_s)
        return _unpack(reply)

def _pause():
    return _rpc("pause")

def _resume():
    return _rpc("resume")

_services_advertised = {}

def advertise(name, address=None, fail_if_exists=False, ttl_s=config.ADVERT_TTL_S):
    """Advertise a name at an address

    Start to advertise service `name` at address `address`. If
    the address is not supplied, one is constructed and this is
    returned by the function. ie this is a typical use::

        address = nw0.advertise("myservice")

    :param name: any text
    :param address: either "ip:port" or None
    :param fail_if_exists: fail if this name is already registered?
    :param ttl_s: the advert will persist for this many seconds other beacons
    :returns: the address given or constructed
    """
    _start_beacon()
    address = _rpc("advertise", name, address, fail_if_exists, ttl_s)
    _services_advertised[name] = address
    return address

def _unadvertise_all():
    """Remove all adverts
    """
    for name in _services_advertised:
        try:
            _unadvertise(name)
        except core.SocketTimedOutError:
            _logger.warn("Timed out trying to unadvertise")
            break
atexit.register(_unadvertise_all)

def _unadvertise(name):
    """Remove the advert for a name

    This is intended for internal use only at the moment. When a process
    exits it can remove adverts for its services from the beacon running
    on that machine. (Of course, if the beacon thread is part of of the
    same service, all its adverts will cease).
    """
    _start_beacon()
    return _rpc("unadvertise", name)

def discover(name, wait_for_s=60):
    """Discover a service by name

    Look for an advert to a named service::

        address = nw0.discover("myservice")

    :param name: any text
    :param wait_for_s: how many seconds to wait before giving up
    :returns: the address found or None
    """
    _start_beacon()
    #
    # It's possible to enter a deadlock situation where the first
    # process fires off a discovery request and waits for the
    # second process to advertise. But the second process has to
    # connect to the rpc port of the first process' beacon and
    # its advertisement is queued behind the pending discovery.
    #
    # To give both a chance of succeeding we operate in bursts,
    # allowing them to interleave.
    #
    t0 = time.time()
    while True:
        discovery = _rpc("discover", name, 0.5)
        if discovery:
            return discovery
        if timed_out(t0, wait_for_s):
            return None

def discover_all(wait_for_s=60):
    """Produce a list of all known services and their addresses

    Ask for all known services as a list of 2-tuples: (name, address)
    This could, eg, be used to form a dictionary of services::

        services = dict(nw0.discover_all())

    :returns: a list of 2-tuples [(name, address), ...]
    """
    _start_beacon()
    #
    # It's possible to enter a deadlock situation where the first
    # process fires off a discovery request and waits for the
    # second process to advertise. But the second process has to
    # connect to the rpc port of the first process' beacon and
    # its advertisement is queued behind the pending discovery.
    #
    # To give both a chance of succeeding we operate in bursts,
    # allowing them to interleave.
    #
    t0 = time.time()
    while True:
        discovery = _rpc("discover_all", 0.5)
        if discovery:
            return discovery
        if timed_out(t0, wait_for_s):
            return None

def discover_group(group, separator="/", exclude=None):
    """Produce a list of all services and their addresses in a group

    A group is an optional form of namespace within the discovery mechanism.
    If an advertised name has the form <group><sep><name> it is deemed to
    belong to <group>. Note that the service's name is still the full
    string <group><sep><name>. The group concept is simply for discovery and
    to assist differentiation, eg, in a classroom group.

    :param group: the name of a group prefix
    :param separator: the separator character [/]
    :param exclude: an iterable of names to exclude (or None)

    :returns: a list of 2-tuples [(name, address), ...]
    """
    _start_beacon()
    if exclude is None:
        names_to_exclude = set()
    else:
        names_to_exclude = set(exclude)
    all_discovered = _rpc("discover_all")
    return [(name, address)
        for (name, address) in all_discovered
        if name.startswith("%s%s" % (group, separator))
        and name not in names_to_exclude
    ]

def reset_beacon():
    """Clear the adverts which the beacon is carrying

    (This is mostly useful when testing, to get a fresh start)
    """
    _start_beacon()
    return _rpc("reset")

if __name__ == '__main__':
    params = [arg.lower() for arg in sys.argv]
    if "--debug" in params:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    handler = logging.StreamHandler()
    handler.setLevel(logging_level)
    handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    _logger.addHandler(handler)
    _start_beacon()
    _logger.info("Beacon started at %s", time.asctime())
    while True:
        time.sleep(1)
