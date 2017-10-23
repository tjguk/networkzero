#!python3
import networkzero as nw0

import logging
logger = logging.getLogger("networkzero")
handler = logging.FileHandler("network.log", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
handler.setLevel(logging.INFO)
logger.addHandler(handler)
del handler, logging
