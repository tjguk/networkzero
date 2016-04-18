try:
    import queue
except ImportError:
    import Queue as queue
import threading

import pytest

import networkzero as nw0
_logger = nw0.core.get_logger("networkzero.tests")
nw0.core._enable_debug_logging()

def support_test_bound_in_other_thread(address, event1):
    #
    # Create a socket in a thread and signal to the test
    # which will try -- and fail -- to create a counterpart
    # listening socket.
    #
    nw0.sockets.get_socket(address, "listener")
    event1.set()

def test_bound_in_other_thread():
    """If a socket is bound in one thread it cannot be
    created and bound in another.
    """
    event1 = threading.Event()
    address = nw0.address()
    t = threading.Thread(target=support_test_bound_in_other_thread, args=(address, event1))
    t.setDaemon(True)
    t.start()
    #
    # Wait until the thread has created its socket otherwise
    # we risk a race condition where the main thread creates
    # first and the exception occurs in the support thread
    #
    event1.wait()
    with pytest.raises(nw0.SocketAlreadyExistsError):
        socket_from_this_thread = nw0.sockets.get_socket(address, "listener")
    t.join()

def support_test_connected_in_other_thread(address, q):
    #
    # Create a socket in a thread which will be a different
    # socket from its counterpart created in the test
    #
    q.put(nw0.sockets.get_socket(address, "speaker"))

def test_connected_in_other_thread():
    """If a sending socket is connected in a different thread, the socket returned
    should be different socket from the equivalent one created in this thread.
    """
    event = threading.Event()
    q = queue.Queue()
    address = nw0.address()
    t = threading.Thread(target=support_test_connected_in_other_thread, args=(address, q))
    t.setDaemon(True)
    t.start()
    socket_from_other_thread = q.get()
    socket_from_this_thread = nw0.sockets.get_socket(address, "speaker")
    assert socket_from_other_thread is not socket_from_this_thread
    t.join()
