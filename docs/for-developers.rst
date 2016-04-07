For Developers
==============

Background
----------

At a club I help at, we've just done a small two-week project
involving three Raspberry Pi boxes: one controlling a motor to drive a
turntable; one detecting hits against targets mounted on the turntable;
and one stopping and starting the turntable and adding up the scores.
They talked to each other over WiFi.

Previously, we entered a robot for PiWars and used WiFi to control
the robot from a laptop with a SNES-like controller attached.

In both cases the use of network was very simple: send a command (START,
STOP, LEFT etc.) possibly with one or more parameters (eg LEFT 0.5).
Under the covers we used ZeroMQ which offers a robust layer on
top of standard sockets. Although ZeroMQ offers a simple and consistent
API, even that's a little too much for newcomers both to networks and
programming.

In addition, a constant challenge was discovering the other "nodes"
on the network in the face of DHCP changes and switching from development
to live networks.

So in the spirit of PyGame Zero and GPIO Zero, I'm offering
Network Zero which depends on ZeroMQ and allows you to:

* Discover services

* Send / Acknowledge commands

* Publish / Subscribe

* Switch painlessly between one and more than one machine

Services
--------

One of the challenges which is particular to the classroom is that you may not
know how to address the box which a service is running on. Even if you
give your boxes static IPs (and you probably don't) or well-known hostnames
then you need some way of knowing easily what IP or name it has. 
If you're using DHCP (and you probably are) then you can't even write the IP 
on a sticky label. All this is exacerbated as kids switch machine between
session and can be as true for a classroom laptop set as much as 
it is for a Raspberry Pi lab.

In addition, the services may be run on the same or a different box which
may be running the same or a different Operating System.

In the robot example above we have two "services": the robot RPi and
the controller laptop. They need to find and talk to each other without knowing
their respective IPs in advance. This is especially true if we are developing
using a local WiFi or even Ethernet setup but testing or running live with
the robot itself becoming an AP.

For the turntable project, we have three RPis: the Turntable listens
for commands; the Detector publishes hits; and the Controller sends commands
and subscribes to hits. For development, we want to run two or more of those 
services on the *same* box, using different processes. 

NB this is a different problem to what DNS solves: we don't want to discover
hosts, we want to discover services, and in a fairly transparent manner. It's
the same kind of problem which zeroconf is solving. [http://www.zeroconf.org/]

Basic Offering
--------------

While the networkzero package will hopefully be of wider use, its
target audience is teachers or organisers of group sessions where
a -- possibly heterogenous -- collection of machines will want to
pass messages simply across a network.

The package offers two things which will be of use to people
running an educational project in a lab situation where machines
and addresses change:

* Advertising and discovery of other programs

* Simple but robust message sending

The first is achieved by having each program fire up a "beacon" which
advertises services by name, indicating the port they are listening on.
Other programs listen for those service adverts until they find the one
they are looking for.

The second uses ZeroMQ socket abstractions to reduce obstacles arising from
the order in which processes start up; and to ensure that messages arrive
complete regardless of network latency &c.

These two are offered independently of each other: the discovery aspect
will leave you with an IP address and a port number. The message aspect
needs an IP address and a port number. But you don't need one to use
the other: it just makes it simpler.


More Information
----------------

.. toctree::
   :maxdepth: 2
   
   design-guidelines
   design-questions
   networkzero
   discovery
   messenger

