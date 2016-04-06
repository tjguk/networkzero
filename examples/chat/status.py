import time
import networkzero as nw0

people = {}
while True:
    #
    # Get a list of all people on the chat and show
    # who's been added since we last looked
    #
    all_people = dict(nw0.discover_all())
    new_people = [name for name in all_people if name not in people]
    if new_people:
        print()
        print("People joined:")
        for name in new_people:
            print(name)

    #
    # Keep our internal list up to date
    #
    people.update(all_people)

    #
    # Listen out for updates from each person in turn
    #
    for person, address in people.items():
        topic, message = nw0.wait_for_notification(address, "chat", wait_for_s=0)
        if topic:
            print("%s says: %s" % (person, message))
    
    #
    # Pause so we don't hog the CPU
    #
    time.sleep(1)