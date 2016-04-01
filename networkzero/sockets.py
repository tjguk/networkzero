# -*- coding: utf-8 -*-
import zmq

from . import config
from . import core
from . import exc
from .logging import logger

class Socket(zmq.Socket):

    def _get_address(self):
        return self._address
    def _set_address(self, address):
        self.__dict__['_address'] = address
        tcp_address = "tcp://%s" % self.address
        if self.type in (zmq.REQ,):
            self.connect(tcp_address)
        elif type in (zmq.REP,):
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
            socket = self._sockets[(caddress, type)] = context.socket(type)
            socket.address = caddress
            self._poller.register(socket)
        return self._sockets[(caddress, type)]
    
    def _receive_with_timeout(self, socket, timeout_secs):
        if timeout_secs is config.FOREVER:
            return socket.recv_string(encoding=config.ENCODING)
        
        sockets = dict(self._poller.poll(1000 * timeout_secs))
        if socket in sockets:
            return socket.recv_string(encoding=config.ENCODING)
        else:
            raise exc.SocketTimedOutError

    def wait_for_request(self, address, wait_for_secs=config.FOREVER):
        socket = self.get_socket(address, zmq.REP)
        return self._receive_with_timeout(socket, wait_for_secs)
        
    def send_request(self, address, request, wait_for_reply_secs=config.FOREVER):
        socket = self.get_socket(address, zmq.REQ)
        socket.send_string(request, encoding=config.ENCODING)
        return self._receive_with_timeout(socket, wait_for_reply_secs)

    def send_reply(self, address, reply):
        socket = self.get_socket(address, zmq.REP)
        return socket.send_string(reply, encoding=config.ENCODING)

_sockets = Sockets()

def get_socket(address, type):
    return _sockets.get_socket(address, type)
