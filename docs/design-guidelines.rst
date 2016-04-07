Design Guidelines
=================

*(Not hard and fast but intended to act as a tiebreaker if needed)*

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
