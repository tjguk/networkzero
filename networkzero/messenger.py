# -*- coding: utf-8 -*-
import shlex

from . import config
from . import core
from . import sockets

_logger = core.get_logger(__name__)

def send_message(address, message, wait_for_reply_s=config.FOREVER):
    """Send a message and return the reply
    
    :param address: a nw0 address (eg from `nw0.discover`)
    :param message: any simple Python object, including text & tuples
    :param wait_for_reply_s: how many seconds to wait for a reply before giving up
    
    :returns: the reply returned from the address or None if out of time
    """
    _logger.debug("Sending message %s to %s for %s secs", message, address, wait_for_reply_s)
    return sockets._sockets.send_message(address, message, wait_for_reply_s)

def wait_for_message(address, wait_for_s=config.FOREVER, autoreply=False):
    """Wait for a message
    
    :param address: a nw0 address (eg from `nw0.advertise`)
    :param wait_for_s: how many seconds to wait for a message before giving up [Forever]
    :param autoreply: automatically send an empty reply? [False]
    
    :returns: the message received from another address or None if out of time
    """
    _logger.debug("Waiting for message on %s for %s secs", address, wait_for_s)
    message = sockets._sockets.wait_for_message(address, wait_for_s)
    if autoreply:
        send_reply(address, None)
    return message

def send_reply(address, reply):
    """Reply to a message previously received
    
    :param address: a nw0 address (eg from `nw0.advertise`)
    :param reply: any simple Python object, including text & tuples
    """
    _logger.debug("Sending reply %s to %s", reply, address)
    return sockets._sockets.send_reply(address, reply)

def send_command(address, command, wait_for_ack_s=config.FOREVER):
    """Send a command to an address and wait for acknowledgement
    
    The command is a single line of text which will be broken out
    into a command followed by parameters. If any of the parameters
    contains a space it needs to be surrounded by quotes, eg::
    
      nw0.send_command(address, "REGISTER person 'Bob Builder'")
    
    :param address: a nw0 address (eg from `nw0.discover`)
    :param command: a line of text
    :param wait_for_ack_s: how many seconds to wait for acknowledgement before giving up
    
    NB Nothing is returned, but a WARNING is logged if no acknowledgement
    is received within `wait_for_ack_s` seconds.
    """
    _logger.debug("Sending command %s to address %s waiting %s secs for an ACK")
    #
    # Let any SocketTimeoutError bubble up; if we haven't received
    # a reply, this socket is effectively unusable.
    #
    ack = send_message(address, command, wait_for_ack_s)
    
    if ack != config.COMMAND_ACK:
        _logger.warn("Unexpected reply %s for command %s to address %s", ack, command, address)

def wait_for_command(address, wait_for_s=config.FOREVER):
    """Wait for a command, acknowledge it and split the command in words
    
    The first word is assumed to be the command; the remaining words are
    the parameters. Typically this would be used like this::
    
      command, params = nw0.wait_for_command(address)
    
    :param address: a nw0 address, eg from `nw0.advertise`
    :param wait_for_s: how many seconds to wait before giving up
    :returns: a 2-tuple (command, [parameters]) or (None, []) if out of time
    """
    _logger.debug("Waiting %s secs for command on %s", wait_for_s, address)
    command = wait_for_message(address, wait_for_s)
    if command is None:
        return None, []
    else:
        send_reply(address, config.COMMAND_ACK)
        components = shlex.split(command)
        return components[0], components[1:]

def send_notification(address, topic, data=None):
    """Publish a notification to all subscribers
    
    :param address: a nw0 address, eg from `nw0.advertise`
    :param topic: any text object
    :param data: any simple Python object including test & tuples
    """
    _logger.debug("Publish topic %s with data %s to %s", topic, data, address)
    return sockets._sockets.send_notification(address, topic, data)

def wait_for_notification(address, prefix=config.EVERYTHING, wait_for_s=config.FOREVER):
    """Wait for notification whose topic starts with `prefix`.
    
    :param address: a nw0 address, eg from `nw0.discover`
    :param prefix: any text object
    :param wait_for_s: how many seconds to wait before giving up
    
    :returns: a 2-tuple of (topic, data) or (None, None) if out of time
    """
    _logger.debug("Listen on %s for notification matching %s waiting for %s secs", address, prefix, wait_for_s)
    return sockets._sockets.wait_for_notification(address, prefix, wait_for_s)
