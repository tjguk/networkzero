import sys
import contextlib
import io
import logging
import queue
import re
import threading
import time
import uuid

import pytest
import zmq

import networkzero as nw0
_logger = nw0.core.get_logger("networkzero.tests")
nw0.core._enable_debug_logging()

class SupportThread(threading.Thread):
    """Fake the other end of the message/command/notification chain
    
    NB we use as little as possible of the nw0 machinery here,
    mostly to avoid the possibility of complicated cross-thread
    interference but also to test our own code.
    """
    
    def __init__(self, context):
        threading.Thread.__init__(self)
        _logger.debug("Init thread")
        self.context = context
        self.queue = queue.Queue()
        self.setDaemon(True)
    
    def run(self):
        try:
            while True:
                test_name, args = self.queue.get()
                if test_name is None:
                    break
                _logger.info("test_support: %s, %s", test_name, args)
                function = getattr(self, "support_test_" + test_name)
                function(*args)
        except:
            _logger.exception("Problem in thread")

    def support_test_send_message(self, address):
        with self.context.socket(zmq.REP) as socket:
            socket.bind("tcp://%s" % address)
            message = nw0.sockets._unserialise(socket.recv())
            socket.send(nw0.sockets._serialise(message))

    def support_test_wait_for_message(self, address, message):
        with self.context.socket(zmq.REQ) as socket:
            socket.connect("tcp://%s" % address)
            _logger.debug("About to send %s", message)
            socket.send(nw0.sockets._serialise(message))
            socket.recv()

    def support_test_send_reply(self, address, queue):
        message = uuid.uuid4().hex
        with self.context.socket(zmq.REQ) as socket:
            socket.connect("tcp://%s" % address)
            socket.send(nw0.sockets._serialise(message))
            reply = nw0.sockets._unserialise(socket.recv())
        queue.put(reply)

    def support_test_send_command(self, address, queue):
        with self.context.socket(zmq.REP) as socket:
            socket.bind("tcp://%s" % address)
            message = nw0.sockets._unserialise(socket.recv())
            components = nw0.split_command(message)
            queue.put((components[0], components[1:]))
            socket.send(nw0.sockets._serialise(nw0.config.COMMAND_ACK))

    def support_test_wait_for_command(self, address, queue):
        action = uuid.uuid4().hex
        param = uuid.uuid4().hex
        command = action + " " + param
        with self.context.socket(zmq.REQ) as socket:
            socket.connect("tcp://%s" % address)
            socket.send(nw0.sockets._serialise(command))
            queue.put((action, [param]))

    def support_test_send_notification(self, address, topic, queue):
        with self.context.socket(zmq.SUB) as socket:
            socket.connect("tcp://%s" % address)
            socket.subscribe = topic.encode("utf-8")
            while True:
                topic, data = nw0.sockets._unserialise_for_pubsub(socket.recv_multipart())
                queue.put((topic, data))
                if data is not None:
                    break

    def support_test_wait_for_notification(self, address, topic, data, sync_queue):
        with self.context.socket(zmq.PUB) as socket:
            socket.bind("tcp://%s" % address)
            while True:
                socket.send_multipart(nw0.sockets._serialise_for_pubsub(topic, None))
                try:
                    sync = sync_queue.get_nowait()
                except queue.Empty:
                    time.sleep(0.1)
                else:
                    break
                
            socket.send_multipart(nw0.sockets._serialise_for_pubsub(topic, data))

@pytest.fixture
def support(request):
    thread = SupportThread(nw0.sockets.context)
    def finalise():
        thread.queue.put((None, None))
        thread.join()
    thread.start()
    return thread

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

#
# send_message
#
#~ @pytest.mark.skipif(sys.version_info[:2] == (2, 7), reason="stalls under 2.7")
def test_send_message(support):
    address = nw0.core.address()
    message = uuid.uuid4().hex
    support.queue.put(("send_message", [address]))
    reply = nw0.send_message(address, message)
    assert reply == message

#
# wait_for_message
#

def test_wait_for_message(support):
    address = nw0.core.address()
    message_sent = uuid.uuid4().hex
    support.queue.put(("wait_for_message", [address, message_sent]))
    message_received = nw0.wait_for_message(address, wait_for_s=5)
    assert message_received == message_sent
    nw0.send_reply(address, message_received)

def test_wait_for_message_with_timeout():
    address = nw0.core.address()
    message = nw0.wait_for_message(address, wait_for_s=0.1)
    assert message is None

#
# send_reply
#
def test_send_reply(support):
    address = nw0.core.address()
    reply_queue = queue.Queue()

    support.queue.put(("send_reply", [address, reply_queue]))
    message_received = nw0.wait_for_message(address, wait_for_s=5)
    nw0.send_reply(address, message_received)
    reply = reply_queue.get()
    assert reply == message_received

#
# send_command
#
def test_send_command(support):
    address = nw0.core.address()
    action = uuid.uuid4().hex
    param = uuid.uuid4().hex
    command = action + " " + param
    reply_queue = queue.Queue()
    
    support.queue.put(("send_command", [address, reply_queue]))
    nw0.send_command(address, command)
    _logger.debug("test_send_command about to read from %s", reply_queue)
    assert reply_queue.get() == (action, [param])

#
# wait_for_command
#
def test_wait_for_command(support):
    address = nw0.core.address()
    reply_queue = queue.Queue()
    
    support.queue.put(("wait_for_command", [address, reply_queue]))
    command_received = nw0.wait_for_command(address, wait_for_s=5)
    assert command_received == reply_queue.get()

#
# send_notification
#
def test_send_notification(support):
    address = nw0.core.address()
    topic = uuid.uuid4().hex
    data = uuid.uuid4().hex
    reply_queue = queue.Queue()
    
    support.queue.put(("send_notification", [address, topic, reply_queue]))
    while True:
        nw0.send_notification(address, topic, None)
        try:
            in_topic, in_data = reply_queue.get_nowait()
        except queue.Empty:
            time.sleep(0.1)
        else:
            break

    nw0.send_notification(address, topic, data)
    while in_data is None:
        in_topic, in_data = reply_queue.get()
    
    assert in_topic, in_data == (topic, data)

#
# wait_for_notification
#
def test_wait_for_notification(support):
    address = nw0.core.address()
    topic = uuid.uuid4().hex
    data = uuid.uuid4().hex
    sync_queue = queue.Queue()
    
    support.queue.put(("wait_for_notification", [address, topic, data, sync_queue]))
    in_topic, in_data = nw0.wait_for_notification(address, topic, wait_for_s=5)
    sync_queue.put(True)
    while in_data is None:
        in_topic, in_data = nw0.wait_for_notification(address, topic, wait_for_s=5)
    assert (topic, data) == (in_topic, in_data)
