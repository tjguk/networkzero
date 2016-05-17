.. currentmodule:: messenger
.. highlight:: python
   :linenothreshold: 1

Exchanging Messages
===================

The examples here all refer to the :mod:`messenger` module.

Send & receive a message
------------------------

Process A
~~~~~~~~~

.. literalinclude:: simple-messaging/send_a_message_a.py

Process B
~~~~~~~~~

.. literalinclude:: simple-messaging/send_a_message_b.py

Discussion
~~~~~~~~~~
The message exchange in networkzero works on a very simple message-reply
model: one process waits for a message from another and sends a reply.
The process sending the original message waits for the reply before carrying
on. This is less flexible that network communications usually are (the
sending process must wait for a reply before carrying on) but cuts out
the complications which arise when several processes are sending messages
to the same listening process.

Send a message without expecting a reply
----------------------------------------

Process A
~~~~~~~~~

.. literalinclude:: simple-messaging/send_a_message_without_reply_a.py

Process B
~~~~~~~~~

.. literalinclude:: simple-messaging/send_a_message_without_reply_b.py

Discussion
~~~~~~~~~~
The message exchange in networkzero always requires a reply to any
message. But sometimes, no reply is needed, for example when sending
commands to a robot. It would be possible for the process which receives 
a message to send a dummy reply and for the process which sent the 
message to ignore any reply.

This situation is so common that there is a special parameter `autoreply`
to the `wait_for_message_from` function. Behind the scenes, networkzero
completes the message-reply contract for you by sending an empty reply.
The process which sent the message can simply ignore any reply.

Send news
---------

Process A
~~~~~~~~~

.. literalinclude:: simple-messaging/send_news_a.py

Process B and C and D...
~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: simple-messaging/send_news_b.py

Discussion
~~~~~~~~~~
One process can send news to any process which is listening. It doesn't
matter if no-one is listening or if 100 other machines are listening. This
could be used, for example, to have one machine linked directly to a 
temperature sensor outside a classroom which broadcasts the temperature once
a minute.

Send news on a specific topic
-----------------------------

Process A
~~~~~~~~~

.. literalinclude:: simple-messaging/send_news_on_topic_a.py

Process B
~~~~~~~~~

.. literalinclude:: simple-messaging/send_news_on_topic_b.py

Process C
~~~~~~~~~

.. literalinclude:: simple-messaging/send_news_on_topic_c.py

Discussion
~~~~~~~~~~
One process can send news on a variety of topics. Other processes can
choose to listen to a specific topic or to all topics. In this example,
Process A is sending news on temperature and humidity. Process B is
listening to the temperature feed while process C is listening to the
data about humidity.