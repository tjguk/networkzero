This example implements a very simple many-to-many
chat system. One of the machines need to run the
hub. (If it finds there's one already running, it
will just shut own again).

Each other machine will need to run two processes:
status.py, which shows who's joined and left and who's
saying what; and chat.py, which enters people into the
chat and sends their messages.

The hub ("chat-hub") receives messages via send_message/wait_for_message 
from the chat processes and sends out notifications ("chat-updates") via
send_notification/wait_for_notification which are picked up by the status
processes.

Obviously a more sophisticated version of this could use pygame or
tkinter windows to display the updates along side the input.