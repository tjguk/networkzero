import sys
import contextlib
import io
import logging
import multiprocessing
import re
import time
import uuid

import pytest

import networkzero as nw0
_logger = nw0.core.get_logger("networkzero.tests")
nw0.core._enable_debug_logging()

context = multiprocessing.get_context("spawn")

@contextlib.contextmanager
def capture_logging(logger, stream):
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    handler.setLevel(logging.WARN)
    logger.addHandler(handler)
    yield
    logger.removeHandler(handler)


@contextlib.contextmanager
def process(function, args):
    p = context.Process(target=function, args=args)
    p.daemon = True
    _logger.debug("About to start process for %s with %s", function, args)
    p.start()
    yield
    p.join()

def check_log(logger, pattern):
    return bool(re.search(pattern, logger.getvalue()))

#
# send_message
#
def support_test_send_message(address):
    nw0.send_reply(address, nw0.wait_for_message(address))

@pytest.mark.skipif(sys.version_info[:2] == (2, 7), reason="stalls under 2.7")
def test_send_message():
    address = nw0.core.address()
    message = uuid.uuid4().hex
    
    with process(support_test_send_message, (address,)):
        reply = nw0.send_message(address, message)
        assert reply == message

#
# wait_for_message
#
def support_test_wait_for_message(address, message):
    _logger.debug("About to send %s to %s")
    nw0.send_message(address, message)

def test_wait_for_message():
    _logger.debug("test_wait_for_message")
    address = nw0.core.address()
    message_sent = uuid.uuid4().hex

    with process(support_test_wait_for_message, (address, message_sent)):
        message_received = nw0.wait_for_message(address)
        nw0.send_reply(address, message_received)
        assert message_received == message_sent

def test_wait_for_message_with_timeout():
    address = nw0.core.address()
    message = nw0.wait_for_message(address, wait_for_s=0.1)
    assert message is None

#
# send_reply
#
def support_test_send_reply(address, queue):
    message = uuid.uuid4().hex
    reply = nw0.send_message(address, message)
    queue.put(reply)

def test_send_reply():
    address = nw0.core.address()
    queue = multiprocessing.Queue()

    #
    # Fire up a remote process which will send a message and then
    # put the reply received (ie from this test) onto a mp queue
    # from which we can retrieve it and check against the message sent
    #
    with process(support_test_send_reply, (address, queue)):
        message_received = nw0.wait_for_message(address)
        nw0.send_reply(address, message_received)
        reply = queue.get()
        assert reply == message_received

#
# send_command
#
def support_test_send_command(address, queue):
    queue.put(nw0.wait_for_command(address))

def test_send_command():
    address = nw0.core.address()
    action = uuid.uuid4().hex
    param = uuid.uuid4().hex
    command = action + " " + param
    queue = multiprocessing.Queue()
    
    with process(support_test_send_command, (address, queue)):
        nw0.send_command(address, command)
        assert queue.get() == (action, [param])

#
# wait_for_command
#
def support_test_wait_for_command(address, queue):
    action = uuid.uuid4().hex
    param = uuid.uuid4().hex
    command = action + " " + param
    queue.put((action, [param]))
    nw0.send_command(address, command)
    
def test_wait_for_command():
    address = nw0.core.address()
    queue = multiprocessing.Queue()

    with process(support_test_wait_for_command, (address, queue)):
        command_received = nw0.wait_for_command(address)
        assert command_received == queue.get()

#
# send_notification
#
def support_test_send_notification(address, topic, queue):
    queue.put("READY")
    topic, data = nw0.wait_for_notification(address, topic, wait_for_s=3)
    queue.put((topic, data))

@pytest.mark.xfail(reason="Unresolved race condition in test")
def test_send_notification():
    address = nw0.core.address()
    topic = uuid.uuid4().hex
    data = uuid.uuid4().hex
    queue = multiprocessing.Queue()
    
    with process(support_test_send_notification, (address, topic, queue)):
        assert "READY" == queue.get()
        nw0.send_notification(address, topic, data)
        assert queue.get() == (topic, data)

#
# wait_for_notification
#
def support_test_wait_for_notification(address, topic, data):
    nw0.send_notification(address, topic, data)

@pytest.mark.xfail(reason="Unresolved race condition in test")
def test_wait_for_notification():
    address = nw0.core.address()
    topic = uuid.uuid4().hex
    data = uuid.uuid4().hex

    with process(support_test_wait_for_notification, (address, topic, data)):
        assert (topic, data) == nw0.wait_for_notification(address, topic, wait_for_s=5)
