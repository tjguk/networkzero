# -*- coding: utf-8 -*-
import json
import time

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

    def __repr__(self):
        return "<Socket %x on %s>" % (id(self), getattr(self, "address", "<No address>"))

    def _get_address(self):
        return self._address
    def _set_address(self, address):
        self.__dict__['_address'] = address
        tcp_address = "tcp://%s" % address
        if self.type in (zmq.REQ, zmq.SUB):
            self.connect(tcp_address)
        elif self.type in (zmq.REP, zmq.PUB):
            self.bind(tcp_address)
        #
        # ZeroMQ has a well-documented feature whereby the
        # newly-added subscriber will always miss the first
        # few posts by a publisher. Just to avoid the surprise,
        # we hackily avoid this here by having each socket
        # wait a short while once it's bound/connected.
        #
        if self.type in (zmq.SUB, zmq.PUB):
            time.sleep(0.5)
    address = property(_get_address, _set_address)

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
    
    def __init__(self):
        self._sockets = {}
    
    def get_socket(self, address, type):
        """Create or retrieve a socket of the right type, already connected
        to the address. Address (ip:port) must be fully specified at this
        point. core.address can be used to generate an address.
        """
        caddress = core.address(address)
        if (caddress, type) not in self._sockets:
            socket = context.socket(type)
            socket.address = caddress
            #
            # Do this last so that an exception earlier will result
            # in the socket not being cached
            #
            self._sockets[(caddress, type)] = socket
        return self._sockets[(caddress, type)]
    
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

    def wait_for_message(self, address, wait_for_s):
        socket = self.get_socket(address, zmq.REP)
        try:
            message = self._receive_with_timeout(socket, wait_for_s)
            return _unserialise(message)
        except (core.SocketTimedOutError):
            return None
        
    def send_message(self, address, request, wait_for_reply_s   ):
        socket = self.get_socket(address, zmq.REQ)
        serialised_request = _serialise(request)
        socket.send(serialised_request)
        return _unserialise(self._receive_with_timeout(socket, wait_for_reply_s))

    def send_reply(self, address, reply):
        socket = self.get_socket(address, zmq.REP)
        reply = _serialise(reply)
        return socket.send(reply)
    
    def send_notification(self, address, topic, data):
        socket = self.get_socket(address, zmq.PUB)
        return socket.send_multipart(_serialise_for_pubsub(topic, data))
    
    def wait_for_notification(self, address, topic, wait_for_s):
        socket = self.get_socket(address, zmq.SUB)
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

def get_socket(address, type):
    return _sockets.get_socket(address, type)
