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