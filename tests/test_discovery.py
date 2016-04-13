try:
    import queue
except ImportError:
    import Queue as queue
import re
import threading
import time
import uuid

import pytest

import networkzero as nw0
_logger = nw0.core.get_logger("networkzero.tests")
nw0.core._enable_debug_logging()

is_valid_ip = nw0.core.is_valid_ip
is_valid_port = nw0.core.is_valid_port
is_valid_address = nw0.core.is_valid_address

class SupportThread(threading.Thread):
    """Fake the other end of the message/command/notification chain
    
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
    nw0.discovery.reset_beacon()

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
