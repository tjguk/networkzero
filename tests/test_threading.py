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

def support_test_used_in_other_thread(address, event):
    _logger.debug("Now in thread %s", threading.current_thread())
    s = nw0.sockets.get_socket(address, "listener")
    _logger.debug("Socket %s from thread %s in thread %s", s, s._thread, threading.current_thread())
    event.wait()

def test_used_in_other_thread():
    _logger.debug("Now in thread %s", threading.current_thread())
    event = threading.Event()
    address = nw0.address()
    t = threading.Thread(target=support_test_used_in_other_thread, args=(address, event))
    t.setDaemon(True)
    t.start()
    with pytest.raises(nw0.DifferentThreadError):
        nw0.wait_for_message(address, wait_for_s=0)
    event.set()
    t.join()
