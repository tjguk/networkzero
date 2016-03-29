networkzero
===========

Make it easy for teachers to use simple networking in Python

[WARNING: Development braindump follows]

Intro
-----

We've just done a small two-week project
involving three Raspberry Pi boxes: one controlling a motor to drive a
turntable; one detecting hits against targets mounted on the turntable;
and one stopping and starting the turntable and adding up the scores.
They talked to each other over WiFi.

Previously, we entered a robot for PiWars and used WiFi to control
the robot from a laptop with a SNES-like controller attached.

In both cases the use of network was very simple: send a command (START,
STOP, LEFT etc.) possibly with one or more parameters (eg LEFT 0.5).
Under the covers we used ZeroMQ which offers a simple but robust layer on
top of standard sockets. Although ZeroMQ offers a simple and consistent
API, even that's a little too much for newcomers both to networks and
programming.

In addition, a constant challenge was discovering the other "nodes"
on the network in the face of DHCP changes and switching from development
to live networks.

So in the spirit of PyGame Zero and GPIO Zero, I'm attempting to offer
Network Zero which depends on ZeroMQ and allows you to:

* Discover services

* Send / Acknowledge commands

* Publish / Subscribe

Services
--------

One of the challenges which is particular to the classroom is that you may not
know how to address the box which a service is running on. Even if you
give your boxes static IPs (and you probably don't) or well-known hostnames
then you need some way of knowing easily what IP or name it has. 
If you're using DHCP (and you probably are) then you can't even write the IP 
on a sticky label. This can be as true for a classroom laptop set as much as 
it is for a Raspberry Pi lab.

In the robot example above we have two "services": the robot RPi and
the controller laptop. They need to find and talk to each other without knowing
their respective IPs in advance. This is especially true if we are developing
using a local WiFi or even Ethernet setup but testing or running live with
the robot itself becoming an AP.

For the turntable project, we have three RPis: the turntable listens
for commands; the detector publishes hits; and the controller sends commands
and subscribes to hits. For development, we want to run two or more of those 
services on the *same* box, using different processes. 

NB this is a different problem to what DNS solves: we don't want to discover
hosts, we want to discover services, and in a fairly ad hoc manner. It's
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
completely regardless of network latency &c.

These two are offered independently of each other: the discovery aspect
will leave you with an IP address and a port number. The message aspect
needs an IP address and a port number. But you don't need one to use
the other: it just makes it simpler.

Possible Questions
------------------

* Do you have to use ZeroMQ? Why not avoid dependencies?

  There's nothing in the design which requires ZeroMQ. The API contract
  hides the implementation. However ZeroMQ does what we need and is 
  available cross-platform with Python bindings.
  
* Why not use [some zeroconf implementation]?

  This is somewhat the converse of the ZeroMQ question above. And the answer
  is similar: there's nothing which precludes the use of using a zeroconf
  solution on a given platform. But cross-platform support is spotty, and
  the services are more designed to support, eg, printer discovery and
  machine discovery. What we're after is a little more ad hoc.
  
  The discovery API is simply advertise / discover. If it turns out that 
  those can be implemented more simply and/or robustly on top of a zeroconf
  service -- or some other existing library -- then we can switch to that
  under the covers.

Intended API
------------

I intend to offer the following (rough) API, subject to change as I
work through things:

address below refers to an IP:Port string eg "192.168.1.5:4567"

Discovery
~~~~~~~~~

* advertise(name, address)

* address = discover(name)

* unadvertise(name[, wait_for_secs=SHORT_WAIT])

Messaging
~~~~~~~~~

* send_command(address, command)

* command = wait_for_command([wait_for_secs=FOREVER])

* make_request(address, question[, wait_for_response_secs=FOREVER])

* question, address = wait_for_request(address, [wait_for_secs=FOREVER])

* send_reply(address, reply)

* publish(address, news)

* wait_for_news(address[, pattern=EVERYTHING][, wait_for_secs=FOREVER])

Questions to be answered
------------------------

* Do we want to allow multiple services to register under the same name?

  This sounds sort of neat, allowing for load-balancing etc. But it raises
  all sorts of complications in the code especially when one of them is removed.
  Although the implementation as I write allows for this, I think on mature reflection
  that it is best left out of a simple package like this.
  
* What happens if the process hosting the Beacon shuts down before the others do

  This is actually less of a problem than it sounds. There are three situations I
  can think of:
  
  1) A new service starts up and want to find an existing service -- this will fail
     because the existing adverts are lost.
  
  2) An existing service wants to use another existing service whose address it has
     previously discovered. This will succeed as long as it no needs to discover
     the address of a named service.
     
  3) An existing service attempts to unadvertise itself, typically on shutdown. This
     will fail, but that failure can be mitigated by having the unadvertise code run
     with a timeout and simply warn if there's no response.

