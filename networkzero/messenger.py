# -*- coding: utf-8 -*-
import shlex

from . import config
from . import core
from . import sockets

_logger = core.get_logger(__name__)

#
# send_message_to(address, wait_for_reply_s)
# send_message_to_any_of([addresses], reply_to=None)
# send_message_to_all_of([addresses], reply_to=None)
# send_reply_to(address)
#
# wait_for_message_on(address, wait_for_s)
#

def send_message_to(address, message, wait_for_reply_s=config.FOREVER):
    """Send a message and return the reply
    
    :param address: a nw0 address (eg from `nw0.discover`) or a list of addresses
    :param message: any simple Python object, including text & tuples
    :param wait_for_reply_s: how many seconds to wait for a reply before giving up
    
    :returns: the reply returned from the address or None if out of time
    """
    _logger.debug("Sending message %s to %s for %s secs", message, address, wait_for_reply_s)
    return sockets._sockets.send_message_to(address, message, wait_for_reply_s)

def wait_for_message_on(address, wait_for_s=config.FOREVER, autoreply=False):
    """Wait for a message
    
    :param address: a nw0 address (eg from `nw0.advertise`)
    :param wait_for_s: how many seconds to wait for a message before giving up [Forever]
    :param autoreply: automatically send an empty reply? [False]
    
    :returns: the message received from another address or None if out of time
    """
    _logger.debug("Waiting for message on %s for %s secs", address, wait_for_s)
    message = sockets._sockets.wait_for_message_on(address, wait_for_s)
    if autoreply and message is not None:
        send_reply_on(address, None)
    return message

def send_reply_on(address, reply):
    """Reply to a message previously received
    
    :param address: a nw0 address (eg from `nw0.advertise`)
    :param reply: any simple Python object, including text & tuples
    """
    _logger.debug("Sending reply %s to %s", reply, address)
    return sockets._sockets.send_reply_on(address, reply)

def send_notification_on(address, topic, data=None):
    """Publish a notification to all subscribers
    
    :param address: a nw0 address, eg from `nw0.advertise`
    :param topic: any text object
    :param data: any simple Python object including test & tuples
    """
    _logger.debug("Publish topic %s with data %s to %s", topic, data, address)
    return sockets._sockets.send_notification_on(address, topic, data)

def wait_for_notification_from(address, prefix=config.EVERYTHING, wait_for_s=config.FOREVER):
    """Wait for notification whose topic starts with `prefix`.
    
    :param address: a nw0 address, eg from `nw0.discover` or a list of addresses
    :param prefix: any text object
    :param wait_for_s: how many seconds to wait before giving up
    
    :returns: a 2-tuple of (topic, data) or (None, None) if out of time
    """
    _logger.debug("Listen on %s for notification matching %s waiting for %s secs", address, prefix, wait_for_s)
    return sockets._sockets.wait_for_notification_from(address, prefix, wait_for_s)
