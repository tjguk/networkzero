# -*- coding: utf-8 -*-
import json
import threading
import time
try:
    string = unicode
except NameError:
    string = str

import zmq

from . import config
from . import core

_logger = core.get_logger(__name__)

def _serialise(message):
    return json.dumps(message).encode(config.ENCODING)

def _unserialise(message_bytes):
    return json.loads(message_bytes.decode(config.ENCODING))

def _serialise_for_pubsub(topic, data):
    topic_bytes = topic.encode(config.ENCODING)
    data_bytes = _serialise(data)
    return [topic_bytes, data_bytes]

def _unserialise_for_pubsub(message_bytes):
    topic_bytes, data_bytes = message_bytes
    return topic_bytes.decode(config.ENCODING), _unserialise(data_bytes)

class Socket(zmq.Socket):

    binding_roles = {"listener", "publisher"}
    
    def __init__(self, *args, **kwargs):
        zmq.Socket.__init__(self, *args, **kwargs)
        #
        # Keep track of which thread this socket was created in
        #
        self.__dict__['_thread'] = threading.current_thread()

    def __repr__(self):
        return "<%s socket %x on %s>" % (self.role, id(self), getattr(self, "address", "<No address>"))

    def _get_address(self):
        return self._address
    def _set_address(self, address):
        _logger.debug("About to set address: %s", address)
        if self.role in self.binding_roles:
            if isinstance(address, (list, tuple)):
                raise core.NetworkZeroError("A listening socket can be bound to only one address, not: %r" % address)
            else:
                self.bind("tcp://%s" % address)
        else:
            if isinstance(address, (list, tuple)):
                addresses = address
            else:
                addresses = [address]
            for a in addresses:
                _logger.debug("About to connect to %s", a)
                self.connect("tcp://%s" % a)
 
        self.__dict__['_address'] = address
        #
        # ZeroMQ has a well-documented feature whereby the
        # newly-added subscriber will always miss the first
        # few posts by a publisher. Just to avoid the surprise,
        # we hackily avoid this here by having each socket
        # wait a short while once it's bound/connected.
        #
        if self.role in ("publisher", "subscriber"):
            time.sleep(0.5)
    address = property(_get_address, _set_address)
    
    def _get_role(self):
        return self._role
    def _set_role(self, role):
        self.__dict__['_role'] = role
    role = property(_get_role, _set_role)

class Context(zmq.Context):
    
    _socket_class = Socket

context = Context()

#
# Global mapping from address to socket. When a socket
# is needed, its address (ip:port) is looked up here. If
# a mapping exists, that socket is returned. If not, a new
# one is created of the right type (REQ / SUB etc.) and
# returned
#
class Sockets:

    try_length_ms = 500 # wait for .5 second at a time
    roles = {
        "listener" : zmq.DEALER,
        "speaker" : zmq.DEALER,
        "publisher" : zmq.PUB,
        "subscriber" : zmq.SUB
    }
    
    def __init__(self):
        self._tls = threading.local()
        self._lock = threading.Lock()
        with self._lock:
            self._sockets = set()
    
    def get_socket(self, address, role):
        """Create or retrieve a socket of the right type, already connected
        to the address. Address (ip:port) must be fully specified at this
        point. core.address can be used to generate an address.
        """
        #
        # If this thread doesn't yet have a sockets cache
        # in its local storage, create one here.
        #
        try:
            self._tls.sockets
        except AttributeError:
            self._tls.sockets = {}
        
        #
        # If a list of addresses is passed, turn it into a tuple
        # of canonical addresses for use as a dictionary key. 
        # Otherwise convert it to a single canonical string.
        #
        if isinstance(address, list):
            caddress = tuple(core.address(a) for a in address)
        else:
            caddress = core.address(address)
            
        #
        # Each socket is identified for this thread by its address(es)
        # and the role the socket is playing (listener, publisher, etc.)
        # That is, within one thread, we are cacheing a read or a write
        # socket to the same address(es).
        #
        # The slight corner case from this is that if you attempt to
        # send to [addressA, addressB] and then to addressA and then
        # to [addressB, addressA], three separate sockets will be
        # created and used.
        #
        identifier = (caddress, role)
        
        if identifier not in self._tls.sockets:
            _logger.debug("%s does not exist in local sockets", identifier)
            #
            # If this is a listening / subscribing socket, it can only
            # be bound once, regardless of thread. Therefore keep a
            # threads-global list of addresses used and make sure this
            # one hasn't been used elsewhere.
            #
            if role in Socket.binding_roles:
                with self._lock:
                    if identifier in self._sockets:
                        raise core.SocketAlreadyExistsError("You cannot create a listening socket in more than one thread")
                    else:
                        self._sockets.add(identifier)
            
            type = self.roles[role]
            socket = context.socket(type)
            socket.role = role
            socket.address = caddress
            #
            # Do this last so that an exception earlier will result
            # in the socket not being cached
            #
            self._tls.sockets[identifier] = socket
        else:
            _logger.debug("%s already not exist in local sockets", identifier)
            #
            # Only return sockets created in this thread
            #
            socket = self._tls.sockets[identifier]

        return socket
    
    def intervals_ms(self, timeout_ms):
        """Generate a series of interval lengths, in ms, which
        will add up to the number of ms in timeout_ms. If timeout_ms
        is None, keep returning intervals forever.
        """
        if timeout_ms is config.FOREVER:
            while True:
                yield self.try_length_ms
        else:
            whole_intervals, part_interval = divmod(timeout_ms, self.try_length_ms)
            for _ in range(whole_intervals):
                yield self.try_length_ms
            yield part_interval

    def _receive_with_timeout(self, socket, timeout_s, use_multipart=False):
        """Check for socket activity and either return what's
        received on the socket or time out if timeout_s expires
        without anything on the socket.
        
        This is implemented in loops of self.try_length_ms milliseconds 
        to allow Ctrl-C handling to take place.
        """
        if timeout_s is config.FOREVER:
            timeout_ms = config.FOREVER
        else:
            timeout_ms = int(1000 * timeout_s)

        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        ms_so_far = 0
        try:
            for interval_ms in self.intervals_ms(timeout_ms):
                sockets = dict(poller.poll(interval_ms))
                ms_so_far += interval_ms
                if socket in sockets:
                    if use_multipart:
                        return socket.recv_multipart()
                    else:
                        return socket.recv()
            else:
                raise core.SocketTimedOutError(timeout_s)
        except KeyboardInterrupt:
            raise core.SocketInterruptedError(ms_so_far / 1000.0)

    def wait_for_message_on(self, address, wait_for_s):
        socket = self.get_socket(address, "listener")
        try:
            message = self._receive_with_timeout(socket, wait_for_s)
        except (core.SocketTimedOutError):
            return None
        else:
            return _unserialise(message)
        
    def send_message_to(self, address, message):
        if isinstance(address, list):
            addresses = address
        else:
            addresses = [address]
        socket = self.get_socket(addresses, "speaker")
        serialised_message = _serialise(message)
        socket.send(serialised_message)

    def send_reply_on(self, address, reply):
        socket = self.get_socket(address, "listener")
        reply = _serialise(reply)
        return socket.send(reply)
    
    def wait_for_reply_from(self, address, wait_for_s):
        if isinstance(address, list):
            addresses = address
        else:
            addresses = [address]
        socket = self.get_socket(addresses, "speaker")
        try:
            message = self._receive_with_timeout(socket, wait_for_s)
        except (core.SocketTimedOutError):
            return None
        else:
            return _unserialise(message)

    def send_notification_on(self, address, topic, data):
        socket = self.get_socket(address, "publisher")
        return socket.send_multipart(_serialise_for_pubsub(topic, data))
    
    def wait_for_notification_from(self, address, topic, wait_for_s):
        if isinstance(address, list):
            addresses = address
        else:
            addresses = [address]
        socket = self.get_socket(addresses, "subscriber")
        if isinstance(topic, str):
            topics = [topic]
        else:
            topics = topic
        for t in topics:
            socket.set(zmq.SUBSCRIBE, t.encode(config.ENCODING))        
        try:
            result = self._receive_with_timeout(socket, wait_for_s, use_multipart=True)
            unserialised_result = _unserialise_for_pubsub(result)
            return unserialised_result
        except (core.SocketTimedOutError, core.SocketInterruptedError):
            return None, None

_sockets = Sockets()

def get_socket(address, role):
    return _sockets.get_socket(address, role)
