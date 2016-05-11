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
    * News: :func:`send_news_to` / :func:`wait_for_news_from`

Functions
---------

Sending Messages
~~~~~~~~~~~~~~~~

Messages are exchanged in a strict request / reply sequence. This restricts
flexibility but makes the semantics obvious. A message is sent to an
address and the process waits until a reply is received. Likewise, a message
is awaited from an address and a reply must be sent before another message
can be received.

The data sent as part of the message will be serialised as JSON so any
object supported by the Python JSON library is a candidate for message payload.

Any number of processes can send a message to one process which is listening.
The messages are sent in a strict request-reply sequence so no ambiguity
should occur.

..  autofunction:: send_message_to
..  autofunction:: wait_for_message_from
..  autofunction:: send_reply_to

Sending News
~~~~~~~~~~~~

News (also known as publications & subscriptions or "pubsub") allows
multiple processes to wait for messages from one (or more) processes. This
is not possible in the message-sending functionality above. There is a notion
of "topics" which allow a publisher to produce a broader range of news
to which a subscriber need only listen for some.

Since a wildcard filter can be used for the topic, the topic used is returned
along with the data when news is received.

..  autofunction:: send_news_to
..  autofunction:: wait_for_news_from
