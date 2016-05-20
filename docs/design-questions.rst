Questions to be answered
========================

* Do you have to use ZeroMQ? Why not avoid dependencies?

  There's nothing in the design which requires ZeroMQ. The API contract
  hides the implementation. However ZeroMQ does what is needed and is 
  available cross-platform and cross-language and with Python bindings.
  
  (Just came across http://nanomsg.org/index.html which is a -- possibly
  unmaintained -- fork of ZeroMQ with a particular eye to Posix-compliance & 
  open licensing).
  
  A couple more factors have been pointed out which tell against using
  ZeroMQ as a dependency:
  
  * The build process, at least for some \*nix, might be daunting
    for teachers unfamiliar with the concepts.
  * It moves the student one step further away from the underlying
    sockets.
  
* Why not use [some zeroconf implementation]?

  This is somewhat the converse of the ZeroMQ question above. And the answer
  is similar, *mutatis mutandis*: there's nothing which precludes the use of using a zeroconf
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
  [**UPDATE**: multiple registration has been removed]
  
  If it were needed, eg in a many-to-many chat situation, it could be implemented
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

  [**UPDATE** Somewhat relevant: time-to-live (TTL) functionality has been added to adverts.
  This means that, if a beacon shuts down, its adverts will expire fairly soon and can be
  replaced by later adverts for the same service. Also, an attempt is made to unadvertise
  when a process shuts down.]

* We have commands as well as messages. Do we need both?

  Perhaps not: under the covers, command is implemented as a message
  which swallows its reply. (Possibly warning if none arrives within a 
  short space of time). But it's likely to be such a common usage pattern 
  that people will usually re-implement it anyway.
  
  [**UPDATE**: I've removed the command functionality, having decided that 
  the value that it brings is not worth the ambiguity it adds to the API. 
  To help in the common case, I've added an autoreply option to 
  :func:`networkzero.wait_for_message_from` and a helper function 
  :func:`networkzero.action_and_params` which will take a text commandline
  and return a command and its params.]

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
  
  [**UPDATE**: We're now using the cross-platform netifaces module as an external
  dependency to determine all local IP4 addresses. We're also allowing
  the :func:`networkzero.address` function to take a wildcard IP so that, for
  example, you could specify that you want a command in the 192.0.2.*
  network without knowing exactly which one you're currently bound to.]
  
  [**UPDATE 2**: accepted a PR from Sandy Wilson to choose the default gateway if
  possible. In combination, we seem to have solved the most common problems around
  selecting the best address.]

* Exceptions or returning None/sentinel?

  Where we have a "soft" error, eg a wait times out, the function called 
  will return a None or some other useful sentinel.

  However if the error is such that no recovery is meaningful, we should raise 
  an exception as usual. In particular, because of the statefulness of ZeroMQ
  sockets, if we don't receive a reply, that socket becomes unusable. [TODO:
  there is the possibility of tracking the state of the underlying socket
  and reacting more helpfully when, a wait is started before a reply is
  sent].
  
  NB This is a pragmatic choice. We're really just dodging the issue knowing
  that, in a classroom situation, we can always bomb out and restart the process.
  In reality, we'd be looking at a zombie socket of some sort, stuck somewhere
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
  
  [**UPDATE**: we're now using JSON to avoid the issue with marshalled
  data not working across different Python versions. This does mean 
  that bytestrings cannot be used directly (nor any other type which
  doesn't support JSON serialisation). For now we've provided a pair
  of bytes<->string converters; later, probably detect this automatically].
  
  pickle has well-known security implications. There are pickle-alikes
  (dill, serpent) in the Python space which do a better job, but they're
  still Python specific. One possibility is to attempt to unserialise 
  with marshal and to fall back to raw bytes if that fails, letting the 
  user decide how to cope with the data.
  
  NB The pubsub stuff has to use bytes because that's how the prefix-matching
  works. [**UPDATE**: pubsub now uses ZeroMQ multipart messages to separate
  out the topic which has to be bytes from the message which can be any
  simple Python object].