import networkzero as nw0

#
# If the hub is already running in another process, drop out
#
hub = nw0.discover("chat-hub", 3)
if hub is not None:
    raise SystemExit("Hub is already running on %s" % hub)

hub = nw0.advertise("chat-hub")
updates = nw0.advertise("chat-updates")
while True:
    action, message = nw0.wait_for_message(hub)
    nw0.send_reply(hub, "OK")
    nw0.send_notification(updates, action, message)
