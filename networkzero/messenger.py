# -*- coding: utf-8 -*-
from . import config
from . import core
from . import sockets

_logger = core.get_logger(__name__)

def send_message_to(address, message):
    """Send a message and return the reply
    
    :param address: a nw0 address (eg from `nw0.discover`) or a list of addresses
    :param message: any simple Python object, including text & tuples
    
    :returns: the reply returned from the address or None if out of time
    """
    _logger.info("Sending message %s to %s", message, address)
    return sockets._sockets.send_message_to(address, message)

def wait_for_message_on(address, wait_for_s=config.FOREVER):
    """Wait for a message
    
    :param address: a nw0 address (eg from `nw0.advertise`)
    :param wait_for_s: how many seconds to wait for a message before giving up [Forever]
    
    :returns: the message received from another address or None if out of time
    """
    _logger.info("Waiting for message on %s for %s secs", address, wait_for_s)
    return sockets._sockets.wait_for_message_on(address, wait_for_s)

def send_reply_on(address, reply):
    """Reply to a message previously received
    
    :param address: a nw0 address (eg from `nw0.advertise`)
    :param reply: any simple Python object, including text & tuples
    """
    _logger.info("Sending reply %s to %s", reply, address)
    return sockets._sockets.send_reply_on(address, reply)

def wait_for_reply_from(address, wait_for_s=config.FOREVER):
    """Wait for a reply from a previously-sent message
    
    :param address: a nw0 address (eg from `nw0.advertise`)
    :param wait_for_s: how many seconds to wait for a message before giving up [Forever]
    
    :returns: any simple Python object, including text & tuples
    """
    _logger.info("Waiting %s for reply from %s", wait_for_s, address)
    return sockets._sockets.wait_for_reply_from(address, wait_for_s)

def send_notification_on(address, topic, data=None):
    """Publish a notification to all subscribers
    
    :param address: a nw0 address, eg from `nw0.advertise`
    :param topic: any text object
    :param data: any simple Python object including test & tuples
    """
    _logger.info("Publish topic %s with data %s to %s", topic, data, address)
    return sockets._sockets.send_notification_on(address, topic, data)

def wait_for_notification_from(address, prefix=config.EVERYTHING, wait_for_s=config.FOREVER):
    """Wait for notification whose topic starts with `prefix`.
    
    :param address: a nw0 address, eg from `nw0.discover` or a list of addresses
    :param prefix: any text object
    :param wait_for_s: how many seconds to wait before giving up
    
    :returns: a 2-tuple of (topic, data) or (None, None) if out of time
    """
    _logger.info("Listen on %s for notification matching %s waiting for %s secs", address, prefix, wait_for_s)
    return sockets._sockets.wait_for_notification_from(address, prefix, wait_for_s)
