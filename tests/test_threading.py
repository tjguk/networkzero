import sys
import contextlib
import io
import logging
try:
    import queue
except ImportError:
    import Queue as queue
import re
import threading
import time
import uuid

import pytest
import zmq

import networkzero as nw0
_logger = nw0.core.get_logger("networkzero.tests")
nw0.core._enable_debug_logging()

def support_test_bound_in_other_thread(address, event):
    #
    # Create a socket in a thread and then pass it back to the test
    # which can assert that it is not the same socket as one created
    # within the test itself
    #
    nw0.sockets.get_socket(address, "listener")
    event.wait()   

def test_bound_in_other_thread():
    """If a socket is bound in one thread it cannot be
    created and bound in another.
    """
    event = threading.Event()
    address = nw0.address()
    t = threading.Thread(target=support_test_bound_in_other_thread, args=(address, event))
    t.setDaemon(True)
    t.start()
    with pytest.raises(nw0.SocketAlreadyExistsError):
        socket_from_this_thread = nw0.sockets.get_socket(address, "listener")
    event.set()
    t.join()

def support_test_connected_in_other_thread(address, q, event):
    q.put(nw0.sockets.get_socket(address, "speaker"))
    event.wait()

def test_connected_in_other_thread():
    """If a sending socket is connected in a different thread, the socket returned
    is a different socket from the equivalent one created in this thread.
    """
    event = threading.Event()
    q = queue.Queue()
    address = nw0.address()
    t = threading.Thread(target=support_test_connected_in_other_thread, args=(address, q, event))
    t.setDaemon(True)
    t.start()
    _logger.debug("other thread started")
    socket_from_other_thread = q.get()
    _logger.debug("other socket: %s", socket_from_other_thread)
    socket_from_this_thread = nw0.sockets.get_socket(address, "speaker")
    _logger.debug("this socket: %s", socket_from_this_thread)
    assert socket_from_other_thread is not socket_from_this_thread
    event.set()
    _logger.debug("Event is set")
    t.join()
    _logger.debug("thread is joined")
