#!python3
import base64
import json

class NetworkZeroEncoder(json.JSONEncoder):
    
    def default(self, obj):
        if isinstance(obj, bytes):
            return (b"\x00" + base64.b64encode(obj)).decode("ascii")
        else:
            return json.JSONEncoder.default(self, obj)

def json_loads_hook(obj):
    print("hook called for", obj)

source = {"data": b"123"}
print("Source: %r" % source)
dumped = json.dumps(source, cls=NetworkZeroEncoder)
print("Dumped: %r" % dumped)
loaded = json.loads(dumped, object_hook=json_loads_hook)
print("Loaded: %r" % loaded)
