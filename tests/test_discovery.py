import re
import time
import uuid

import pytest

import networkzero as nw0
nw0.core._setup_debug_logging()

is_valid_ip = nw0.core.is_valid_ip
is_valid_port = nw0.core.is_valid_port
is_valid_address = nw0.core.is_valid_address

@pytest.fixture
def beacon(request):
    nw0.discovery._start_beacon()
    request.addfinalizer(nw0.discovery.stop_beacon)

def test_advertise_no_address(beacon):
    service = uuid.uuid1().hex
    address = nw0.advertise(service)
    assert is_valid_address(address)
    assert (service, address) in nw0.discover_all()
    nw0.discovery.stop_beacon()

def test_advertise_no_port(beacon):
    service = uuid.uuid1().hex
    address = nw0.advertise(service)
    assert is_valid_address(address, port_range=nw0.config.DYNAMIC_PORTS)
    assert (service, address) in nw0.discover_all()

def test_advertise_full_address(beacon):
    service = uuid.uuid1().hex
    service_address = "192.168.1.1:1234"
    address = nw0.advertise(service, service_address)
    assert address == service_address
    assert (service, address) in nw0.discover_all()

def test_discover(beacon):
    service = uuid.uuid1().hex
    address = nw0.advertise(service)
    assert address == nw0.discover(service)

def test_discover_not_exists_with_timeout(beacon):
    service = uuid.uuid1().hex
    address = nw0.advertise(service)
    assert None is nw0.discover(uuid.uuid1().hex, wait_for_secs=2)

def test_discover_exists_with_timeout(beacon):
    service = uuid.uuid1().hex
    address = nw0.advertise(service)
    assert address == nw0.discover(service, wait_for_secs=2)

def test_discover_all(beacon):
    service1 = uuid.uuid1().hex
    address1 = nw0.advertise(service1)
    service2 = uuid.uuid1().hex
    address2 = nw0.advertise(service2)
    services = dict(nw0.discover_all())
    assert services == {service1:address1, service2:address2}
