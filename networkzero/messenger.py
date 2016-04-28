# -*- coding: utf-8 -*-
from . import config
from . import core
from . import sockets

_logger = core.get_logger(__name__)
AUTOREPLY = None

def send_message_to(address, message, wait_for_reply_s=config.FOREVER):
    """Send a message and return the reply
    
    :param address: a nw0 address (eg from `nw0.discover`)
    :param message: any simple Python object, including text & tuples
    :param wait_for_reply_s: how many seconds to wait for a reply [default: forever]
    
    :returns: the reply returned from the address or None if out of time
    """
    _logger.info("Sending message %s to %s", message, address)
    if isinstance(address, list):
        raise core.InvalidAddressError("Multiple addresses are not allowed")
    return sockets._sockets.send_message_to(address, message, wait_for_reply_s)

def wait_for_message_from(address, wait_for_s=config.FOREVER, autoreply=False):
    """Wait for a message
    
    :param address: a nw0 address (eg from `nw0.advertise`)
    :param wait_for_s: how many seconds to wait for a message before giving up [default: forever]
    :param autoreply: whether to send an empty reply [default: No]
    
    :returns: the message received from another address or None if out of time
    """
    _logger.info("Waiting for message on %s for %s secs", address, wait_for_s)
    message = sockets._sockets.wait_for_message_from(address, wait_for_s)
    if message is not None and autoreply:
        sockets._sockets.send_reply_to(address, AUTOREPLY)
    return message

def send_reply_to(address, reply):
    """Reply to a message previously received
    
    :param address: a nw0 address (eg from `nw0.advertise`)
    :param reply: any simple Python object, including text & tuples
    """
    _logger.debug("Sending reply %s to %s", reply, address)
    return sockets._sockets.send_reply_to(address, reply)

def send_notification_to(address, topic, data=None):
    """Publish a notification to all subscribers
    
    :param address: a nw0 address, eg from `nw0.advertise`
    :param topic: any text object
    :param data: any simple Python object including test & tuples [default: empty]
    """
    _logger.info("Publish topic %s with data %s to %s", topic, data, address)
    return sockets._sockets.send_notification_to(address, topic, data)

def wait_for_notification_from(address, prefix=config.EVERYTHING, wait_for_s=config.FOREVER):
    """Wait for notification whose topic starts with `prefix`.
    
    :param address: a nw0 address, eg from `nw0.discover`
    :param prefix: any text object [default: all messages]
    :param wait_for_s: how many seconds to wait before giving up [default: forever]
    
    :returns: a 2-tuple of (topic, data) or (None, None) if out of time
    """
    _logger.info("Listen on %s for notification matching %s waiting for %s secs", address, prefix, wait_for_s)
    return sockets._sockets.wait_for_notification_from(address, prefix, wait_for_s)
