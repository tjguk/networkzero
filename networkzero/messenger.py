# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)
from . import config
from . import core
from . import exc
from . import sockets

"""
* send_command(address, command)

* command = wait_for_command([wait_for_secs=FOREVER])

* send_message(address, question[, wait_for_response_secs=FOREVER])

* question, address = wait_for_message([wait_for_secs=FOREVER])

* send_response(address, response)

* publish_news(address, news)

* wait_for_news(address[, pattern=EVERYTHING, wait_for_secs=FOREVER])
"""

def send_message(address, message, wait_for_reply_secs=config.FOREVER):
    _logger.debug("Sending message %s to %s for %s secs", message, address, wait_for_reply_secs)
    return sockets._sockets.send_message(address, message, wait_for_reply_secs)

def wait_for_message(address, wait_for_secs=config.FOREVER):
    _logger.debug("Waiting for message on %s for %s secs", address, wait_for_secs)
    return sockets._sockets.wait_for_message(address, wait_for_secs)

def send_reply(address, reply):
    return sockets._sockets.send_reply(address, reply)

def send_command(address, command, wait_for_reply_secs=config.FOREVER):
    try:
        reply = send_message(address, command, wait_for_reply_secs)
    except exc.SocketTimedOutError:
        _logger.warn("No reply received for command %s to address %s", command, address)
    
    if reply != config.COMMAND_ACK:
        _logger.warn("Unexpected reply %s for command %s to address %s", reply, command, address)

def wait_for_command(address, callback, wait_for_secs=config.FOREVER):
    command = wait_for_message(address, wait_for_secs)
    send_reply(address, config.COMMAND_ACK)
    callback(command)

def publish_news(address, news):
    raise NotImplementedError

def wait_for_news(address, pattern=config.EVERYTHING, wait_for_secs=config.FOREVER):
    raise NotImplementedError
