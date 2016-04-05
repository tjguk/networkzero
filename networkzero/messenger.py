# -*- coding: utf-8 -*-
from . import config
from . import core
from . import sockets

_logger = core.get_logger(__name__)

def send_message(address, message, wait_for_reply_secs=config.FOREVER):
    """Send a message to an address and return the reply
    
    :param address: a nw0 address (eg from `nw0.discover`)
    :param message: any simple Python object, including text & tuples
    :param wait_for_reply_secs: how many seconds to wait for a reply before giving up
    
    :returns: the reply returned from the address
    """
    _logger.debug("Sending message %s to %s for %s secs", message, address, wait_for_reply_secs)
    return sockets._sockets.send_message(address, message, wait_for_reply_secs)

def wait_for_message(address, wait_for_secs=config.FOREVER):
    """Wait for a message from another address
    
    :param address: a nw0 address (eg from `nw0.advertise`)
    :param wait_for_secs: now many seconds to wait for a message before giving up
    
    :returns: the message received from another address or None if timeout
    """
    _logger.debug("Waiting for message on %s for %s secs", address, wait_for_secs)
    return sockets._sockets.wait_for_message(address, wait_for_secs)

def send_reply(address, reply):
    """Reply to a message which has arrived at this address
    
    :param address: a nw0 address (eg from `nw0.advertise`)
    :param reply: any simple Python object, including text & tuples
    """
    _logger.debug("Sending reply %s to %s", reply, address)
    return sockets._sockets.send_reply(address, reply)

def send_command(address, command, wait_for_ack_secs=config.FOREVER):
    """Send a command to an address and wait for acknowledgement
    
    NB this differs from `send_message` only by virtue of not expecting
    a reply, only acknowledgement that the message has been received.
    
    :param address: a nw0 address (eg from `nw0.discover`)
    :param message: any simple Python object, including text & tuples
    :param wait_for_ack_secs: how many seconds to wait for acknowledgement before giving up    
    """
    _logger.debug("Sending command %s to address %s waiting %s secs for an ACK")
    try:
        ack = send_message(address, command, wait_for_ack_secs)
    except core.SocketTimedOutError:
        _logger.warn("No reply received for command %s to address %s", command, address)
    
    if ack != config.COMMAND_ACK:
        _logger.warn("Unexpected reply %s for command %s to address %s", ack, command, address)

def wait_for_command(address, callback, wait_for_secs=config.FOREVER):
    """Wait for a command and issue a callback
    
    :param address: a nw0 address, eg from `nw0.advertise`
    :param callback: a function to be called with the command received
    :param wait_for_secs: how many seconds to wait before giving up
    """
    _logger.debug("Waiting %s secs for command on %s with callback %s", wait_for_secs, address, callback)
    command = wait_for_message(address, wait_for_secs)
    send_reply(address, config.COMMAND_ACK)
    callback(command)

def send_notification(address, notification):
    """Publish a notification to all subscribers
    
    :param address: a nw0 address, eg from `nw0.advertise`
    :param notification: any text object
    """
    _logger.debug("Publish %s to %s", notification, address)
    return sockets._sockets.send_notification(address, notification)

def wait_for_notification(address, prefix=config.EVERYTHING, wait_for_secs=config.FOREVER):
    """Wait for notification starting with `prefix`
    
    :param address: a nw0 address, eg from `nw0.discover`
    :param prefix: any text object
    :param wait_for_secs: how many seconds to wait before giving up
    
    :returns: the notification received or `None` if timeout
    """
    _logger.debug("Listen on %s for notification matching %s waiting for %s secs", address, prefix, wait_for_secs)
    return sockets._sockets.wait_for_notification(address, prefix, wait_for_secs)
