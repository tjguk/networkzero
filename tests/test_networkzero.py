import re

import pytest

import networkzero as nw0

def split_address(address):
    ip, _, port = address.partition(":")
    return ip, port

def is_valid_ip(ip):
    return bool(re.match("^\d{,3}\.\d{,3}\.\d{,3}\.\d{,3}$", ip))

def is_valid_port(port, port_range=range(65536)):
    try:
        return int(port) in port_range
    except ValueError:
        return False

def is_valid_address(address, port_range=range(65536)):
    ip, port = split_address(address)
    return is_valid_ip(ip) and is_valid_port(port, port_range)

def test_import_all_revelant_names():
    all_names = {
        "advertise", "unadvertise", "discover", "discover_all",
        "send_command", "wait_for_command", 
        "send_message", "wait_for_message", "send_reply", 
        "publish_news", "wait_for_news",
    }
    #
    # Find all the names imported into the nw0 package except
    # the submodules which are implictly imported.
    #
    nw0_names = set(
        name 
            for name in dir(nw0) 
            if not name.startswith("_") and 
            type(getattr(nw0, name)) != type(nw0)
    )
    assert not all_names - nw0_names, "Mismatch: %s" % (all_names - nw0_names)
    assert not nw0_names - all_names, "Mismatch: %s" % (nw0_names - all_names)

class TestAddress(object):

    def test_none_supplied(self):
        canonical_address = nw0.core.address()
        assert is_valid_address(canonical_address, port_range=nw0.config.DYNAMIC_PORTS)

    def test_valid_ip_supplied(self):
        address = "127.0.0.1"
        canonical_address = nw0.core.address(address)
        assert is_valid_address(canonical_address)
    
    def test_valid_port_string_is_supplied(self):
        address = "1234"
        canonical_address = nw0.core.address(address)
        assert is_valid_address(canonical_address)
    
    def test_valid_port_int_is_supplied(self):
        address = 1234
        canonical_address = nw0.core.address(address)
        assert is_valid_address(canonical_address)

    def test_valid_port_zero_is_supplied(self):
        address = 0
        canonical_address = nw0.core.address(address)
        assert is_valid_address(canonical_address, port_range=nw0.config.DYNAMIC_PORTS)

    def test_valid_both_are_supplied(self):
        address = "127.0.0.1:1234"
        canonical_address = nw0.core.address(address)
        assert is_valid_address(canonical_address)

    def test_invalid_ip_supplied(self):
        address = "INVALID"
        with pytest.raises(nw0.core.InvalidAddressError):
            canonical_address = nw0.core.address(address)

    def test_invalid_port_supplied(self):
        address = 123456
        with pytest.raises(nw0.core.InvalidAddressError):
            canonical_address = nw0.core.address(address)

    def test_invalid_both_supplied(self):
        address = "INVALID:INVALID"
        with pytest.raises(nw0.core.InvalidAddressError):
            canonical_address = nw0.core.address(address)
