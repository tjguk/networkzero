import re

import pytest

import networkzero as nw0

def test_import_all_revelant_names():
    all_names = {
        "advertise", "unadvertise", "discover", "discover_all",
        "send_command", "wait_for_command", 
        "send_message", "wait_for_message", "send_reply", 
        "publish_news", "wait_for_news",
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

