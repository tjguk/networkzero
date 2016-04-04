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
