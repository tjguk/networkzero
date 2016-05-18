import os, sys
import tempfile
import networkzero as nw0

address = nw0.advertise("gallery")
while True:
    filename, data = nw0.wait_for_message_from(address, autoreply=True)
    bytes = nw0.string_to_bytes(data)
    
    temp_filepath = os.path.join(tempfile.gettempdir(), filename)
    with open(temp_filepath, "wb") as f:
        f.write(data)
    print("Wrote", temp_filepath)
