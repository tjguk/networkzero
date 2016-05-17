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