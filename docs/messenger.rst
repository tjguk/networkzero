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

    * Messages: :func:`send_message_to` / :func:`wait_for_message_from`
    * Notifications: :func:`send_notification_to` / :func:`wait_for_notification_from`

Functions
---------

Sending Messages
~~~~~~~~~~~~~~~~
..  autofunction:: send_message_to
..  autofunction:: wait_for_message_from

Sending Notifications
~~~~~~~~~~~~~~~~~~~~~
..  autofunction:: send_notification_to
..  autofunction:: wait_for_notification_from
