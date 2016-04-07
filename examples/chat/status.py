import networkzero as nw0

updates = nw0.discover("chat-updates")
while True:
    action, message = nw0.wait_for_notification(updates)
    print(action, message)
    if action == "JOIN":
        print("%s has joined" % message)
    elif action == "LEAVE":
        print("%s has left" % message)
    elif action == "SPEAK":
        [person, words] = message
        print("%s says: %s" % (person, words))
    else:
        print("!! Unexpected message: %s" % message)
