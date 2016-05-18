import base64
import re
import uuid
    
import pytest

import networkzero as nw0
nw0.core._enable_debug_logging()

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
            nw0.core.address(address)

    def test_invalid_port_supplied(self):
        address = 123456
        with pytest.raises(nw0.core.AddressError):
            nw0.core.address(address)

    def test_invalid_both_supplied(self):
        address = "!!!:INVALID"
        with pytest.raises(nw0.core.AddressError):
            nw0.core.address(address)
    
    def test_valid_ip_pattern_supplied(self):
        address = "127.*"
        canonical_address = nw0.core.address(address)
        assert is_valid_address(canonical_address)
    
    def test_invalid_ip_pattern_supplied(self):
        address = "255.*"
        with pytest.raises(nw0.core.AddressError):
            nw0.core.address(address)

class TestCommand(object):
    
    def test_action_only(self):
        commandline = "ACTION"
        assert nw0.core.action_and_params(commandline) == ("ACTION", [])
    
    def test_action_and_one_param(self):
        commandline = "ACTION PARAM1"
        assert nw0.core.action_and_params(commandline) == ("ACTION", ["PARAM1"])
    
    def test_action_and_several_params(self):
        commandline = "ACTION PARAM1 PARAM2 PARAM3"
        assert nw0.core.action_and_params(commandline) == ("ACTION", ["PARAM1", "PARAM2", "PARAM3"])
    
    def test_param_with_space(self):
        commandline = "ACTION 'PARAM 1'"
        assert nw0.core.action_and_params(commandline) == ("ACTION", ["PARAM 1"])

class TestBytesToString(object):

    bytes = uuid.uuid1().hex.encode("ascii")
    string = base64.b64encode(bytes).decode("ascii")
    
    def test_string_to_bytes(self):
        b = nw0.core.string_to_bytes(self.string)
        assert isinstance(b, bytes)
        assert b == self.bytes

    def test_bytes_to_string(self):
        s = nw0.core.bytes_to_string(self.bytes)
        assert isinstance(s, str)
        assert s == self.string
    
    def test_reflection_from_bytes(self):
        assert nw0.core.string_to_bytes(nw0.core.bytes_to_string(self.bytes)) == self.bytes
    
    def test_reflection_from_string(self):
        assert nw0.core.bytes_to_string(nw0.core.string_to_bytes(self.string)) == self.string