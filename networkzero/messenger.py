# -*- coding: utf-8 -*-
from . import config
from . import core
from . import exc
from . import sockets
from .logging import logger

"""
* send_command(address, command)

* command = wait_for_command([wait_for_secs=FOREVER])

* send_message(address, question[, wait_for_response_secs=FOREVER])

* question, address = wait_for_message([wait_for_secs=FOREVER])

* send_response(address, response)

* publish_news(address, news)

* wait_for_news(address[, pattern=EVERYTHING, wait_for_secs=FOREVER])
"""

def send_message(address, request, wait_for_reply_secs=config.FOREVER):
    logger.debug("Sending request %s to %s for %s secs", request, address, wait_for_reply_secs)
    return sockets._sockets.send_message(address, request, wait_for_reply_secs)

def wait_for_message(address, wait_for_secs=config.FOREVER):
    logger.debug("Waiting for request on %s for %s secs", address, wait_for_secs)
    return sockets._sockets.wait_for_message(address, wait_for_secs)

def send_reply(address, reply):
    return sockets._sockets.send_reply(address, reply)

def send_command(address, command, wait_for_reply_secs=config.FOREVER):
    try:
        reply = send_message(address, command, wait_for_reply_secs)
    except exc.SocketTimedOutError:
        logger.warn("No reply received for command %s to address %s", command, address)

def wait_for_command(address, callback, wait_for_secs=config.FOREVER):
    command = wait_for_message(address, wait_for_secs)
    reply = callback(command)
    return send_reply(address, reply)

def publish_news(address, news):
    raise NotImplementedError

def wait_for_news(address, pattern=config.EVERYTHING, wait_for_secs=config.FOREVER):
    raise NotImplementedError
