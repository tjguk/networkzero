# -*- coding: utf-8 -*-
"""
* send_command(address, command)

* command = wait_for_command([wait_for_secs=FOREVER])

* make_request(address, question[, wait_for_response_secs=FOREVER])

* question, address = wait_for_request([wait_for_secs=FOREVER])

* send_response(address, response)

* publish(address, news)

* wait_for_news(address[, pattern=EVERYTHING, wait_for_secs=FOREVER])
"""
import zmq

import .config
from .core import context
import .exc
from .logging import logger

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
    
    def get_socket(self, address, type):
        socket = self._sockets.get(address)
        if socket is not None:
            if socket.type != type:
                raise exc.SocketAlreadyExistsError(address, type, socket.type)
        else:
            socket = self._sockets[address] = core.context.socket(type)
        return socket
    
    def get_request_socket(self, address):
        return self.get_socket(address, zmq.REQ)

def send_command(address, command):
    raise NotImplementedError

def wait_for_command(wait_for_secs=config.FOREVER):
    raise NotImplementedError

def make_request(address, request, wait_for_response_secs=config.FOREVER):
    raise NotImplementedError

def wait_for_request(address, wait_for_secs=config.FOREVER):
    raise NotImplementedError

def send_reply(address, reply):
    raise NotImplementedError

def publish(address, news):
    raise NotImplementedError

def wait_for_news(address, pattern=config.EVERYTHING, wait_for_secs=config.FOREVER)
    raise NotImplementedError

_sockets = Sockets()
