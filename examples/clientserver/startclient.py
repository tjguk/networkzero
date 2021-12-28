'''Simple script to start a networzero client and send a message to a server on the network. Useful for troubleshooting/or simple demos in a classroom environment.
'''

import networkzero as nw0

hello = nw0.discover("hello")
reply = nw0.send_message_to(hello, "World!")
print(reply)
reply = nw0.send_message_to(hello, "Tim")
print(reply)
