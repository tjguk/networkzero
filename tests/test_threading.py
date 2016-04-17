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

def support_test_used_in_other_thread(address, q):
    #
    # Create a socket in a thread and then pass it back to the test
    # which can assert that it is not the same socket as one created
    # within the test itself
    #
    q.put(nw0.sockets.get_socket(address, "listener"))

def test_used_in_other_thread():
    _logger.debug("Now in thread %s", threading.current_thread())
    q = queue.Queue()
    address = nw0.address()
    t = threading.Thread(target=support_test_used_in_other_thread, args=(address, q))
    t.setDaemon(True)
    t.start()
    socket_from_other_thread = q.get()
    socket_from_this_thread = nw0.sockets.get_socket(address, "listener")
    assert socket_from_this_thread is not socket_from_other_thread
    t.join()
