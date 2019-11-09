import sys
import networkzero as nw0

try:
    # Python 2.7 compat
    input = raw_input
except NameError:
    pass

print("Looking for chat hub")
hub = nw0.discover("chat-hub")
if not hub:
    print("Unable to find chat hub after 60s")
    raise SystemExit

print("Chat hub found at", hub)

def main(name=None):
    name = name or input("Name: ")
    nw0.send_message_to(hub, ["JOIN", name])
    try:
        while True:
            try:
                message = input("Message: ")
            except KeyboardInterrupt:
                message = None
            if not message:
                break
            nw0.send_message_to(hub, ["SPEAK", (name, message)])
    finally:
        nw0.send_message_to(hub, ["LEAVE", name])

if __name__ == '__main__':
    main(*sys.argv[1:])
