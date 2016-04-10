Sending & Receiving Messages
============================

..  automodule:: networkzero.messenger
    :synopsis: Sending & receiving messages across the network
    :show-inheritance:
..  moduleauthor:: Tim Golden <mail@timgolden.me.uk>


Introduction
------------

The messenger module offers two ways to send and/or receive messages across
the network:

    * Messages: :func:`send_message` / :func:`wait_for_message`
    * Notifications: :func:`send_notification` / :func:`wait_for_notification`

Functions
---------

Sending Messages
~~~~~~~~~~~~~~~~
..  autofunction:: send_message
..  autofunction:: wait_for_message

Sending Notifications
~~~~~~~~~~~~~~~~~~~~~
..  autofunction:: send_notification
..  autofunction:: wait_for_notification
