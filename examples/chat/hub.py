import networkzero as nw0

#
# If the hub is already running in another process, drop out
#
hub = nw0.discover("chat-hub", 3)
if hub is not None:
    raise SystemExit("Hub is already running on %s" % hub)

hub = nw0.advertise("chat-hub")
print("Hub on", hub)
updates = nw0.advertise("chat-updates")
print("Updates on", updates)
while True:
    action, params = nw0.wait_for_message_from(hub)
    print("Action: %s, Params: %s" % (action, params))
    nw0.send_notification_to(updates, action, params)
