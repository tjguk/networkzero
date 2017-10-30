..  module:: networkzero

Installation
============

Introduction
------------

NetworkZero is designed to be used in an educational context, so it targets the Raspberry Pi,
but you should be able to install it anywhere that runs Python. This can be a good choice for
experimenting with what it can do on your own laptop (see whether it's right for your next
workshop), for example.

Dependencies
------------

NetworkZero has two external dependencies:

* PyZMQ
* netifaces

Getting these dependencies is a little bit different on each platform, so see whether you can
find yours below. Once you've done the bit for your platform, go on down to `Get NetworkZero`_.

Raspberry Pi
~~~~~~~~~~~~

Todo:

* Verify the below.

::

    sudo apt-get install zeromq

You should be good to go - head on down to `Get NetworkZero`_.

Windows
~~~~~~~

Todo:

* Write instructions for getting libzeromq installed.
* PyZMQ and netifaces have wheels available.

Once you've got these set up, head on down to `Get NetworkZero`_.

MacOS
~~~~~

Todo:

* Write instructions for getting libzeromq installed.
* PyZMQ has wheels available
* netifaces will need source installation as there's no wheel - so macos's equivalent of build-essential is probably required.

Linux
~~~~~

On Linux, there are a few dependencies that you'll need to have installed so that you can run the setup.

Fedora: ::

    # Common tools for building and installing python packages on Linux
    sudo dnf install gcc gcc-c++ python-devel redhat-rpm-config

    # ZeroMQ's native library
    sudo dnf install zeromq

That shoud be everything - head on down to `Get NetworkZero`_.

Get NetworkZero
---------------

::

    pip install networkzero

Now, check that it's installed correctly. You should get something like the following: ::

    python -c 'import networkzero'

If that returns without an error you're good to go! You can move on. If that doesn't work,
check that there were no errors or warnings when running the setup commands in previous
sections. If there were - and you can figure out what went wrong - try fixing those up and
trying again. If not, please let us know - it's probably easiest to
`file an issue<https://github.com/tjguk/networkzero/issues>`.
