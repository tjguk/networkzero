# -*- coding: utf-8 -*-
import zmq

from . import config
from . import core
from . import exc
from .logging import logger

class Socket(object):

    def __init__(self, socket):
        self.__dict__['_socket'] = socket
    
    def __getattr__(self, attr):
        return getattr(self._socket, attr)
    
    def __setattr__(self, attr, value):
        setattr(self._socket, attr, value)
    
    def _get_address(self):
        return urllib.parse.parse(self._socket.last_endpoint).netloc
    address = property(_get_address)

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
        to the address
        """
        caddress = core.address(address)

        socket = self._sockets.get(caddress)
        if socket is not None:
            if socket.type == type:
                return socket
            else:
                raise exc.SocketAlreadyExistsError(caddress, type, socket.type)
        
        socket = Socket(core.context.socket(type))
        ip, _, port = caddress.partition(":")
        if port == "0":
            port = socket.bind_to_random_port("tcp://%s" % ip)
            caddress = "%s:%s" % (ip, port)
            socket.unbind("tcp://%s" % caddress)
        
        if type in (zmq.REQ,):
            socket.connect("tcp://%s" % caddress)
        elif type in (zmq.REP,):
            socket.bind("tcp://%s" % caddress)
        if type in (zmq.REQ, zmq.REP):
            self._poller.register(socket._socket)

        self._sockets[caddress] = socket
        return socket
    
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
