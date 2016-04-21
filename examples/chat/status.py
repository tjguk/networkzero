import networkzero as nw0

print("Looking for chat updates channel")
updates = nw0.discover("chat-updates")
if not updates:
    print("Unable to find chat updates channel after 60s")
    raise SystemExit

print("Chat updates found at", updates)    
while True:
    action, message = nw0.wait_for_notification_from(updates)
    if action is None:
        break
    elif action == "JOIN":
        print("%s has joined" % message)
    elif action == "LEAVE":
        print("%s has left" % message)
    elif action == "SPEAK":
        [person, words] = message
        print("%s says: %s" % (person, words))
    else:
        print("!! Unexpected message: %s" % message)
