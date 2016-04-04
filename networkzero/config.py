# -*- coding: utf-8 -*-
"""Common configuration elements for networkzero
"""
ENCODING = "UTF-8"
class _Forever(object):
    def __repr__(self): return "∞"
FOREVER = _Forever()
SHORT_WAIT = 1 # 1 second
EVERYTHING = ""
COMMAND_ACK = "ack"
BEACON_ADVERT_FREQUENCY_SECS = 2

VALID_PORTS = range(0x10000)
DYNAMIC_PORTS = range(0xC000, 0x10000)
