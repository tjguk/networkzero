import logging

logger = logging.getLogger("network")
logger.setLevel(logging.DEBUG)
#
# FIXME: for now, just throw some useful file logging in
#
handler = logging.FileHandler("network.log")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
