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
    
def test_send_message():
    address = nw0.core.address()
    message = uuid.uuid1().hex
    
    #
    # Fire up a remote process to echo back any message received.
    # Then check that the message we receive back is the same as
    # the one which went out.
    #
    p = multiprocessing.Process(target=support_test_send_message, args=(address,), daemon=True)
    p.start()
    reply = nw0.send_message(address, message)
    assert reply == message
    p.join()

def test_wait_for_message():
    address = nw0.core.address()
    message_sent = uuid.uuid1().hex

    #
    # Start an external process which will send a message without waiting
    # for a reply
    #
    p = multiprocessing.Process(target=nw0.send_message, args=(address, message_sent, 0), daemon=True)
    p.start()
    message_received = nw0.wait_for_message(address)
    assert message_received == message_sent
    p.join()

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
    p = multiprocessing.Process(target=support_test_send_reply, args=(address, queue), daemon=True)
    p.start()
    message_received = nw0.wait_for_message(address)
    nw0.send_reply(address, message_received)
    reply = queue.get()
    assert reply == message_received
    p.join()

def test_send_command():
    address = nw0.core.address()
    action = uuid.uuid1().hex
    param = uuid.uuid1().hex
    command = action + " " + param
    queue = multiprocessing.Queue()
    
    #
    # Fire up a remote process to ack any command received.
    #
    p = multiprocessing.Process(target=support_test_send_command, args=(address, queue), daemon=True)
    p.start()
    nw0.send_command(address, command)
    assert queue.get() == (action, [param])
    p.join()

def test_wait_for_command():
    address = nw0.core.address()
    queue = multiprocessing.Queue()

    p = multiprocessing.Process(target=support_test_wait_for_command, args=(address, queue), daemon=True)
    p.start()
    command_received = nw0.wait_for_command(address)
    assert command_received == queue.get()
    p.join()
