# -*- coding: utf-8 -*-
"""Common configuration elements for networkzero
"""
ENCODING = "UTF-8"
class _Forever(object):
    def __repr__(self): return "<Forever>"
FOREVER = _Forever()
SHORT_WAIT = 1 # 1 second
EVERYTHING = ""
COMMAND_ACK = "ack"
#
# Beacons will broadcast adverts at this frequency
#
BEACON_ADVERT_FREQUENCY_S = 5
#
# Adverts will expire after this many seconds unless
# a fresh broadcast is received. Default it above the
# broadcast frequency so adverts are not forever expiring
# and being recreated by the next received broadcast.
#
ADVERT_TTL_S = 3 * BEACON_ADVERT_FREQUENCY_S

VALID_PORTS = range(0x10000)
DYNAMIC_PORTS = range(0xC000, 0x10000)
