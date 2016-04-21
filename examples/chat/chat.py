import networkzero as nw0

print("Looking for chat hub")
hub = nw0.discover("chat-hub")
if not hub:
    print("Unable to find chat hub after 60s")
    raise SystemExit

print("Chat hub found at", hub)

name = input("Name: ")
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
