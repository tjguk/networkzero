#!python3
import zmq
import networkzero as nw0

import logging
handler = logging.FileHandler("network.log")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
nw0.logging.logger.addHandler(handler)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
nw0.logging.logger.addHandler(handler)
del handler, logging

