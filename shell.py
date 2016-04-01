#!python3
import os, sys
import logging

import networkzero as nw0

address = "127.0.0.1:1234"

#
# FIXME: for now, just throw some useful file logging in
#
handler = logging.FileHandler("network.log")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
nw0.logging.logger.addHandler(handler)
