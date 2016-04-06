import contextlib
import io
import logging
import multiprocessing
import re
import time
import uuid

import pytest

import networkzero as nw0
nw0.core._setup_debug_logging()

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
    p = multiprocessing.Process(target=function, args=args, daemon=True)
    p.start()
    yield
    p.join()

def check_log(logger, pattern):
    return bool(re.search(pattern, logger.getvalue()))

def support_test_send_message(address):
    nw0.send_reply(address, nw0.wait_for_message(address))

def support_test_send_reply(address, queue):
    message = uuid.uuid1().hex
    reply = nw0.send_message(address, message)
    queue.put(reply)

def support_test_send_command(address, queue):
    queue.put(nw0.wait_for_command(address))

def support_test_wait_for_command(address, queue):
    action = uuid.uuid1().hex
    param = uuid.uuid1().hex
    command = action + " " + param
    queue.put((action, [param]))
    nw0.send_command(address, command)
    
def support_test_send_notification(address, topic, queue):
    queue.put("READY")
    topic, data = nw0.wait_for_notification(address, topic, wait_for_s=3)
    queue.put((topic, data))

def test_send_message():
    address = nw0.core.address()
    message = uuid.uuid1().hex
    
    with process(support_test_send_message, (address,)):
        reply = nw0.send_message(address, message)
        assert reply == message

def test_wait_for_message():
    address = nw0.core.address()
    message_sent = uuid.uuid1().hex

    with process(nw0.send_message, (address, message_sent, 0)):
        message_received = nw0.wait_for_message(address)
        assert message_received == message_sent

def test_wait_for_message_with_timeout():
    address = nw0.core.address()
    message = nw0.wait_for_message(address, wait_for_s=0.1)
    assert message is None

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

def test_send_command():
    address = nw0.core.address()
    action = uuid.uuid1().hex
    param = uuid.uuid1().hex
    command = action + " " + param
    queue = multiprocessing.Queue()
    
    with process(support_test_send_command, (address, queue)):
        nw0.send_command(address, command)
        assert queue.get() == (action, [param])

def test_wait_for_command():
    address = nw0.core.address()
    queue = multiprocessing.Queue()

    with process(support_test_wait_for_command, (address, queue)):
        command_received = nw0.wait_for_command(address)
        assert command_received == queue.get()

def test_send_notification():
    address = nw0.core.address()
    topic = uuid.uuid1().hex
    data = uuid.uuid1().hex
    queue = multiprocessing.Queue()
    
    with process(support_test_send_notification, (address, topic, queue)):
        assert "READY" == queue.get()
        for i in range(10):
            nw0.send_notification(address, topic, data)
        assert queue.get() == (topic, data)
