# -*- coding: utf-8 -*-
import marshal

import zmq

from . import config
from . import core

_logger = core.get_logger(__name__)

def _serialise(message):
    return marshal.dumps(message)

def _unserialise(message_bytes):
    return marshal.loads(message_bytes)

class Socket(zmq.Socket):

    def __repr__(self):
        return "<Socket %x on %s>" % (id(self), getattr(self, "address", "<No address>"))

    def _get_address(self):
        return self._address
    def _set_address(self, address):
        self.__dict__['_address'] = address
        tcp_address = "tcp://%s" % address
        if self.type in (zmq.REQ,):
            self.connect(tcp_address)
        elif self.type in (zmq.REP,):
            self.bind(tcp_address)
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

    def __init__(self):
        self._sockets = {}
        self._poller = zmq.Poller()
    
    def get_socket(self, address, type):
        """Create or retrieve a socket of the right type, already connected
        to the address. Address (ip:port) must be fully specified at this
        point. core.address can be used to generate an address.
        """
        caddress = core.address(address)
        if (caddress, type) not in self._sockets:
            socket = context.socket(type)
            socket.address = caddress
            self._poller.register(socket)
            #
            # Do this last so that an exception earlier will result
            # in the socket not being cached
            #
            self._sockets[(caddress, type)] = socket
        return self._sockets[(caddress, type)]
    
    def _receive_with_timeout(self, socket, timeout_secs):
        if timeout_secs is config.FOREVER:
            return socket.recv()
        
        sockets = dict(self._poller.poll(1000 * timeout_secs))
        if socket in sockets:
            return socket.recv()
        else:
            raise core.SocketTimedOutError

    def wait_for_message(self, address, wait_for_secs=config.FOREVER):
        socket = self.get_socket(address, zmq.REP)
        _logger.debug("socket %s waiting for request", socket)
        try:
            return _unserialise(self._receive_with_timeout(socket, wait_for_secs))
        except core.SocketTimedOutError:
            _logger.warn("Socket %s timed out after %s secs", socket, wait_for_secs)
            return None
        
    def send_message(self, address, request, wait_for_reply_secs=config.FOREVER):
        socket = self.get_socket(address, zmq.REQ)
        socket.send(_serialise(request))
        try:
            return _unserialise(self._receive_with_timeout(socket, wait_for_reply_secs))
        except core.SocketTimedOutError:
            _logger.warn("Socket %s timed out after %s secs", socket, wait_for_secs)
            return None            

    def send_reply(self, address, reply):
        socket = self.get_socket(address, zmq.REP)
        return socket.send(_serialise(reply))

_sockets = Sockets()

def get_socket(address, type):
    return _sockets.get_socket(address, type)
