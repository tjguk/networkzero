import multiprocessing
import re
import time
import uuid

import pytest

import networkzero as nw0
nw0.core._setup_debug_logging()

def echo_message(address):
    import networkzero as nw0
    nw0.send_reply(address, nw0.wait_for_message(address))

def check_reply(address, queue):
    import networkzero as nw0
    import uuid
    message = uuid.uuid1().hex
    reply = nw0.send_message(address, message)
    queue.put(reply)

def test_send_message():
    address = nw0.core.address()
    message = uuid.uuid1().hex
    
    #
    # Fire up a remote process to echo back any message received.
    # Then check that the message we receive back is the same as
    # the one which went out.
    #
    p = multiprocessing.Process(target=echo_message, args=(address,), daemon=True)
    p.start()
    reply = nw0.send_message(address, message)
    p.join()
    assert reply == message

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
    p.join()
    assert message_received == message_sent

def test_send_reply():
    address = nw0.core.address()
    queue = multiprocessing.Queue()

    #
    # Fire up a remote process which will send a message and then
    # put the reply received (ie from this test) onto a mp queue
    # from which we can retrieve it and check against the message sent
    #
    p = multiprocessing.Process(target=check_reply, args=(address, queue), daemon=True)
    p.start()
    message_received = nw0.wait_for_message(address)
    nw0.send_reply(address, message_received)
    reply = queue.get()
    p.join()
    assert reply == message_received
