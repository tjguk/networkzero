networkzero
===========

Make it easy for learning groups to use simple networking in Python

Intended API
------------

I intend to offer the following (rough) API, subject to change as I
work through things:

address below refers to an IP:Port string eg "192.168.1.5:4567"

Discovery
~~~~~~~~~

* address = advertise(name, address=None)

* address = discover(name, wait_for_secs)

* unadvertise(name[, wait_for_secs=SHORT_WAIT])

* [(name, address), ...] = discover_all()

Messaging
~~~~~~~~~

* send_command(address, command)

* command = wait_for_command([wait_for_secs=FOREVER])

* send_message(address, question[, wait_for_response_secs=FOREVER])

* question, address = wait_for_request(address, [wait_for_secs=FOREVER])

* send_reply(address, reply)

* publish_news(address, news)

* wait_for_news(address[, pattern=EVERYTHING][, wait_for_secs=FOREVER])

[WARNING: Development braindump follows]

Typical Usage
-------------

On computer (or process) A::

    import networkzero as nw0
    
    address = nw0.advertise("hello")
    while True:
        name = nw0.wait_for_message(address)
        nw0.send_reply(address, "Hello, %s" % name)
        
On computer (or process) B::

    import networkzero as nw0
    
    hello = nw0.discover("hello")
    reply = nw0.send_message(hello, "World")
    print(reply)
    reply = nw0.send_message(hello, "Tim")
    print(reply)

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

Design Guidelines
-----------------

(ie tiebreakers if we need to make a decision)

* networkzero is aimed at beginners and particularly at those in an 
  educational setting (classroom, Raspberry Jam etc.)
  
* If you need more than this, you'll want to drop down to ZeroMQ itself,
  or some other library, and implement your own. Or at least use the
  internals of networkzero directly.

* The preference is for module-level functions rather than objects.
  (Behind the scenes, global object caches are used)

* As much as possible, code should work in the interactive interpreter
  
* Thread-safety is not a priority
  
* Code will work unchanged on one box and on several.

* Code will work unchanged on Linux, OS X & Windows, assuming
  that the pre-requisites are met (basically: recent Python & zmqlib).
  
* Code will work unchanged on Python 2.7 and Python 3.2+

* The discovery & messenger modules are uncoupled: neither relies on 
  or knows about the internals of the other.
  
* All useful functions & constants are exported from the root of the package
  so either "import networkzero as nw0" or "from networkzero import *"
  will provide the whole of the public API.

* Underscore prefixes will be used to ensure that only the public API 
  be visible via help(). This reduces visual clutter.

Questions to be answered
------------------------

* Do you have to use ZeroMQ? Why not avoid dependencies?

  There's nothing in the design which requires ZeroMQ. The API contract
  hides the implementation. However ZeroMQ does what we need and is 
  available cross-platform and cross-language and with Python bindings.
  
* Why not use [some zeroconf implementation]?

  This is somewhat the converse of the ZeroMQ question above. And the answer
  is similar: there's nothing which precludes the use of using a zeroconf
  solution on a given platform. But cross-platform support is spotty, and
  it's more geared towards, eg, printer discovery and machine discovery. 
  What we're after is a little more ad hoc and transient.
  
  The discovery API is simply advertise / discover. If it turns out that 
  those can be implemented more simply and/or robustly on top of a zeroconf
  service -- or some other existing library -- then we can switch to that
  under the covers.

* Do we want to allow multiple services to register under the same name?

  This sounds sort of neat, allowing for load-balancing etc. But it raises
  all sorts of complications in the code especially when one of them is removed.
  Although the implementation as I write allows for this, I think on mature 
  reflection that it is best left out of a simple package like this.
  [*UPDATE*: multiple registration has been removed]
  
  If were needed, eg in a many-to-many chat situation, it could be implemented
  fairly easily on top of networkzero by defining a "service:<GUID>" naming
  convention to distinguish related by distinct services.
  
* What happens if the process hosting the Beacon shuts down before the others do?

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

* We have commands as well as messages. Do we need both?

  Perhaps not: under the covers, command is implemented as a message
  which swallows its reply. (Possibly warning if none arrives within a 
  short space of time). But it's likely to be such a common usage pattern 
  that people will usually re-implement it anyway.

* What about multi IP addresses?

  My dev machine has a VM setup with its host-only network. More plausibly
  for the classroom it's quite possible to have, eg, an RPi connected both
  to wired & wireless networks at the same time. At present, we're only
  choosing one IP address. Our options seem to be:
  
  i) Let the user deal with it: deactivate IP addresses which are not
     wanted for the purposes (eg host-only addresses).
    
  ii) Have some sort of config.ini which allows users to disregard or prefer
      certain addresses or networks
    
  iii) Allow the "address" object to be more than one address in a list.
       These multiple addresses will then be advertised and messages sent
       across them.
    
  Of course, a combination of these could be used. Just for now, we can
  defer deciding as most machines, at least in the classroom, will have 
  only one IP address at a time. My slight preference is for (iii) as I see
  it being fairly easy to implement and fairly transparent.

* Exceptions or returning None/sentinel?

  Where we have a "soft" error, eg a command is sent but no ack is received
  within the expected timeframe, we should carry on with a warning. As it
  stands warnings and above are logged to stderr so will usually be visible
  to users. In these cases, the function called will return a None instead
  of the ack/reply which was expected.

  However if the error is such that no recovery is meaningful, we should raise 
  an exception as usual: if, for example, an invalid IP address or port number
  is used for an address.
  
  NB This is a pragmatic choice. We're really just dodging the issue knowing
  that, in a classroom situation, we can always bomb out and restart the process.
  In reality, we'd be looking at a zombie socket of some sort, stuck somwhere
  inside its own state machine.
  
* We currently used marshal to serialise messages. Is this a good idea?

  Possibly not: the advantage is that it handles simple objects in a
  consistent way [although not necessarily across Python versions, it
  occurs to me]. The obvious alternatives are:
  
    * Bytes: let the user encode
    * JSON/YAML
    * pickle
    * A.N.Other serialisation protocol

  The actual serialisation is transparent to users; however, the current
  implementation allows simple Python structures without any extra effort. 
  So someone can pass a tuple of values or a dictionary. Or a unicode 
  string / byte string.
  
  The downside to this is that code written for ZeroMQ but in another
  language will struggle to match this. (Obviously it would be possible, but
  far more trouble than it was worth). JSON would be an obvious x-platform
  alternative but, when I tried it, gave some difficulties over encoding.
  (Waves hands; I can't remember exactly what the issue was...)
  
  pickle has well-known security implications. There are pickle-alikes
  (dill, serpent) in the Python space which do a better job, but they're
  still Python specific.
  
  One possibility is to attempt to unserialise with marshal and to fall
  back to raw bytes if that fails, letting the user decide how to cope
  with the data.
