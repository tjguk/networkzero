import networkzero as nw0

hub = nw0.discover("chat-hub")
print("Hub found on", hub)
updates = nw0.discover("chat-updates")
print("Updates found on", updates)

name = input("Name: ")
nw0.send_message(hub, ["JOIN", name])
try:
    while True:
        message = input("Message: ")
        if not message:
            break
        nw0.send_message(hub, ["SPEAK", (name, message)])
finally:
    nw0.send_message(hub, ["LEAVE", name])
