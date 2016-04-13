import re

import pytest

import networkzero as nw0
nw0.core._enable_debug_logging()

def test_import_all_relevant_names():
    all_names = {
        "advertise", "discover", "discover_all", "discover_group",
        "send_message", "wait_for_message", "send_reply", 
        "send_notification", "wait_for_notification",
        "action_and_params", "address",
        "NetworkZeroError", "SocketAlreadyExistsError",
        "SocketTimedOutError", "InvalidAddressError",
        "SocketInterruptedError"
    }
    #
    # Find all the names imported into the nw0 package except
    # the submodules which are implictly imported.
    #
    nw0_names = set(
        name 
            for name in dir(nw0) 
            if not name.startswith("_") and 
            type(getattr(nw0, name)) != type(nw0)
    )
    assert not all_names - nw0_names, "Mismatch: %s" % (all_names - nw0_names)
    assert not nw0_names - all_names, "Mismatch: %s" % (nw0_names - all_names)

