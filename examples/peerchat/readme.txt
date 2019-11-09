This example implements a very simple hub-based (ie not peer-to-peer)
chat system. One machine needs to start the hub. (If there's one already
running, it will just shut down again).

Each other machine will need to run two processes:

* status.py shows who's joined and left and who's saying what
* chat.py enters people into the chat and publishes the messages the type

The hub (advertised as "chat-hub") receives messages via send_message/wait_for_message
from the chat processes and sends out notifications (advertised as "chat-updates") which
are picked up via send_notification/wait_for_notification by the status processes.

Obviously a more sophisticated version of this could use pygame or
tkinter windows to display the updates along side the input.