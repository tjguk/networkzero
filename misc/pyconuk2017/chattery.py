import os, sys

import networkzero as nw0

if __name__ == '__main__':
    people = []

    chattery = nw0.advertise("chattery")

    while True:
        message = nw0.wait_for_message_from(chattery)
        action, params = nw0.action_and_params(message)
        action = action.upper()
        if action == "JOIN":
            name = params[0]
            code = "-".join(name.lower().split())
            people.append("chattery/%s" % code)

        elif action == "LEAVE":
        elif action == "SAY":
        else:
            print("Unknown command: %s" % action)
