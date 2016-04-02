#!python3
import zmq
import networkzero as nw0

import logging
logger = logging.getLogger("networkzero")
handler = logging.FileHandler("network.log", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
del handler, logging
