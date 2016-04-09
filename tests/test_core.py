import re

import pytest

import networkzero as nw0
nw0.core._enable_debug_logging()

is_valid_ip = nw0.core.is_valid_ip
is_valid_port = nw0.core.is_valid_port
is_valid_address = nw0.core.is_valid_address

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
        address = "!!!"
        with pytest.raises(nw0.core.InvalidAddressError):
            canonical_address = nw0.core.address(address)

    def test_invalid_port_supplied(self):
        address = 123456
        with pytest.raises(nw0.core.AddressError):
            canonical_address = nw0.core.address(address)

    def test_invalid_both_supplied(self):
        address = "INVALID:INVALID"
        with pytest.raises(nw0.core.AddressError):
            canonical_address = nw0.core.address(address)
