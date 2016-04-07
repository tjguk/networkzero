Sending & Receiving Messages
============================

..  automodule:: networkzero.messenger
    :synopsis: Sending & receiving messages across the network
    :show-inheritance:
..  moduleauthor:: Tim Golden <mail@timgolden.me.uk>


Introduction
------------

The messenger module offers three way to send and/or receive messages across
the network:

    * Messages: :func:`send_message` / :func:`wait_for_message`
    * Commands: :func:`send_command` / :func:`wait_for_command`
    * Notifications: :func:`send_notification` / :func:`wait_for_notification`

Functions
---------

Sending Messages
~~~~~~~~~~~~~~~~
..  autofunction:: send_message
..  autofunction:: wait_for_message

Sending Commands
~~~~~~~~~~~~~~~~
..  autofunction:: send_command
..  autofunction:: wait_for_command

Sending Notifications
~~~~~~~~~~~~~~~~~~~~~
..  autofunction:: send_notification
..  autofunction:: wait_for_notification
