.. currentmodule:: messenger
.. highlight:: python
   :linenothreshold: 1

Exchanging Messages: Advanced Usage
===================================

The examples here all refer to the :mod:`messenger` module.

News from more than one source
------------------------------

Process A, B, C and D
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: advanced-messaging/news_from_multiple_sources_abcd.py

Process E
~~~~~~~~~

.. literalinclude:: advanced-messaging/news_from_multiple_sources_e.py

Discussion
~~~~~~~~~~
A process can listen for news from more than one source. For example,
if you have four movement sensors, one in each corner of a room, all
ending their updates on the same channel, you can gather updates from
all four at once.

Sending Data
------------

Process A
~~~~~~~~~

.. literalinclude:: advanced-messaging/sending_data_a.py

Process B
~~~~~~~~~

.. literalinclude:: advanced-messaging/sending_data_b.py

Discussion
~~~~~~~~~~

Sometimes the data you want to send isn't text or numbers: it's binary data
-- bytes -- such as the bytes which make up an image or a sound file. To send that via
networkzero you have to treat it specially: at the sending end, you convert
it to a string; and at the receiving end, you convert it back into bytes.