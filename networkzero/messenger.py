# -*- coding: utf-8 -*-
from . import config
from . import core
from . import sockets

_logger = core.get_logger(__name__)

def send_message(address, message, wait_for_reply_secs=config.FOREVER):
    _logger.debug("Sending message %s to %s for %s secs", message, address, wait_for_reply_secs)
    return sockets._sockets.send_message(address, message, wait_for_reply_secs)

def wait_for_message(address, wait_for_secs=config.FOREVER):
    _logger.debug("Waiting for message on %s for %s secs", address, wait_for_secs)
    return sockets._sockets.wait_for_message(address, wait_for_secs)

def send_reply(address, reply):
    _logger.debug("Sending reply %s to %s", reply, address)
    return sockets._sockets.send_reply(address, reply)

def send_command(address, command, wait_for_ack_secs=config.FOREVER):
    _logger.debug("Sending command %s to address %s waiting %s secs for an ACK")
    try:
        ack = send_message(address, command, wait_for_ack_secs)
    except core.SocketTimedOutError:
        _logger.warn("No reply received for command %s to address %s", command, address)
    
    if ack != config.COMMAND_ACK:
        _logger.warn("Unexpected reply %s for command %s to address %s", ack, command, address)

def wait_for_command(address, callback, wait_for_secs=config.FOREVER):
    _logger.debug("Waiting %s secs for command on %s with callback %s", wait_for_secs, address, callback)
    command = wait_for_message(address, wait_for_secs)
    send_reply(address, config.COMMAND_ACK)
    callback(command)

def publish_news(address, news):
    _logger.debug("Publish %s to %s", news, address)
    raise NotImplementedError

def wait_for_news(address, pattern=config.EVERYTHING, wait_for_secs=config.FOREVER):
    _logger.debug("Listen on %s for news matching %s waiting for %s secs", address, pattern, wait_for_secs)
    raise NotImplementedError
