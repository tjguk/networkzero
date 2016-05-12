try:
    import queue
except ImportError:
    import Queue as queue
import random
import re
import socket
import threading
import time
import uuid

import pytest

import networkzero as nw0
_logger = nw0.core.get_logger("networkzero.tests")
nw0.core._enable_debug_logging()

is_valid_port = nw0.core.is_valid_port
is_valid_address = nw0.core.is_valid_address

class SupportThread(threading.Thread):
    """Fake the other end of the message/command/news chain
    
    NB we use as little as possible of the nw0 machinery here,
    mostly to avoid the possibility of complicated cross-thread
    interference but also to test our own code.
    """
    
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.context = context
        self.queue = queue.Queue()
        self.setDaemon(True)
    
    def run(self):
        try:
            while True:
                test_name, args = self.queue.get()
                if test_name is None:
                    break
                function = getattr(self, "support_test_" + test_name)
                function(*args)
        except:
            _logger.exception("Problem in thread")

    def support_test_discover_before_advertise(self, service):
        time.sleep(1)
        nw0.advertise(service)

@pytest.fixture
def support(request):
    thread = SupportThread(nw0.sockets.context)
    def finalise():
        thread.queue.put((None, None))
        thread.join()
    thread.start()
    return thread

@pytest.fixture
def beacon(request):
    port = random.choice(nw0.config.DYNAMIC_PORTS)
    nw0.discovery._start_beacon(port=port)
    request.addfinalizer(nw0.discovery.reset_beacon)

def test_beacon_already_running():
    #
    # NB this one has to run without the beacon fixture
    #
    # Bind a socket on a random port before attempting
    # to start a beacon on that same port.
    #
    port = random.choice(nw0.config.DYNAMIC_PORTS)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(("", port))
    try:
        assert nw0.discovery._beacon is None
        nw0.discovery._start_beacon(port=port)
        assert nw0.discovery._beacon is nw0.discovery._remote_beacon
    finally:
        s.close()
        #
        # Make sure any future beacon use assumes it's not
        # already running.
        #
        nw0.discovery._stop_beacon()

def test_advertise_no_address(beacon):
    service = uuid.uuid4().hex
    address = nw0.advertise(service)
    assert is_valid_address(address)
    assert [service, address] in nw0.discover_all()

def test_advertise_no_port(beacon):
    service = uuid.uuid4().hex
    address = nw0.advertise(service)
    assert is_valid_address(address, port_range=nw0.config.DYNAMIC_PORTS)
    assert [service, address] in nw0.discover_all()

def test_advertise_full_address(beacon):
    service = uuid.uuid4().hex
    service_address = "192.168.1.1:1234"
    address = nw0.advertise(service, service_address)
    assert address == service_address
    assert [service, address] in nw0.discover_all()

def test_advertise_ttl(beacon):
    service = uuid.uuid4().hex
    ttl_s = 5
    address = nw0.advertise(service, ttl_s=ttl_s)
    assert [service, address] in nw0.discover_all()
    #
    # Stop advert broadcast for long enough that any
    # stale ones will be expired
    # 
    nw0.discovery._pause()
    try:
        time.sleep(1 + ttl_s)
        assert [service, address] not in nw0.discover_all()
    finally:
        nw0.discovery._resume()

def test_unadvertise(beacon):
    ttl_s = 2
    service = uuid.uuid4().hex
    address = nw0.advertise(service, ttl_s=ttl_s)
    assert [service, address] in nw0.discover_all()
    nw0.discovery._unadvertise(service)
    time.sleep(1 + ttl_s)
    assert [service, address] not in nw0.discover_all()

def test_discover(beacon):
    service = uuid.uuid4().hex
    address = nw0.advertise(service)
    assert address == nw0.discover(service)

def test_discover_not_exists_with_timeout(beacon):
    service = uuid.uuid4().hex
    address = nw0.advertise(service)
    assert None is nw0.discover(uuid.uuid4().hex, wait_for_s=2)

def test_discover_exists_with_timeout(beacon):
    service = uuid.uuid4().hex
    address = nw0.advertise(service)
    assert address == nw0.discover(service, wait_for_s=2)

def test_discover_all(beacon):
    service1 = uuid.uuid4().hex
    address1 = nw0.advertise(service1)
    service2 = uuid.uuid4().hex
    address2 = nw0.advertise(service2)
    services = dict(nw0.discover_all())
    assert services == {service1:address1, service2:address2}

def test_discover_before_advertise(beacon, support):
    service1 = uuid.uuid4().hex
    support.queue.put(("discover_before_advertise", [service1]))
    address1 = nw0.discover(service1, wait_for_s=5)
    assert address1 is not None

def test_discover_group(beacon):
    group = uuid.uuid4().hex
    service1 = "%s/%s" % (group, uuid.uuid4().hex)
    service2 = "%s/%s" % (group, uuid.uuid4().hex)
    service3 = "%s/%s" % (uuid.uuid4().hex, uuid.uuid4().hex)
    address1 = nw0.advertise(service1)
    address2 = nw0.advertise(service2)
    address3 = nw0.advertise(service3)
    discovered_group = nw0.discover_group(group)
    assert set(discovered_group) == set([(service1, address1), (service2, address2)])

def test_discover_group_with_different_separator(beacon):
    group = uuid.uuid4().hex
    service1 = "%s:%s" % (group, uuid.uuid4().hex)
    service2 = "%s:%s" % (group, uuid.uuid4().hex)
    service3 = "%s:%s" % (uuid.uuid4().hex, uuid.uuid4().hex)
    address1 = nw0.advertise(service1)
    address2 = nw0.advertise(service2)
    address3 = nw0.advertise(service3)
    discovered_group = nw0.discover_group(group, separator=":")
    assert set(discovered_group) == set([(service1, address1), (service2, address2)])

def test_rpc_with_timeout():
    """Access to the local beacon is via an RPC mechanism using 
    ZeroMQ REQ-REP sockets. If the beacon has stopped, this will block.
    This is especially problematic when an attempt is being made to
    unadvertise services via the atexit.register mechanism.
    """
    #
    # Make sure the beacon is not running and attempt an RPC
    # connection with a timeout
    #
    nw0.discovery._stop_beacon()
    with pytest.raises(nw0.core.SocketTimedOutError):
        nw0.discovery._rpc(uuid.uuid4().hex, wait_for_s=2)

def _test_unadvertise_with_timeout():
    """Adverts are unadvertised when a process exits (via atexit.register).
    However, if the local beacon has already stopped, any attempt to send
    it a message will block.
    """
    #
    # Start a beacon on a random port and register an arbitrary
    # service. We need to know neither the port nor the service;
    # all we do is check unadvertising will succeed.
    #
    nw0.discovery._start_beacon(port=random.choice(nw0.config.DYNAMIC_PORTS))
    nw0.advertise(uuid.uuid4().hex)
    nw0.discovery._stop_beacon()
    