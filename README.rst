A Python Library for Generating dbus-python Client Code
=======================================================

Introduction
------------
This library contains a few methods that consume an XML specification of
a D-Bus interface and return classes or functions that may be useful in
constructing a dbus-python based D-Bus client. The XML specification has the
format of the data returned by the Introspect() method of the Introspectable
interface.

Methods
-------

* gmo_reader_builder:
  This function consumes the spec for a single interface and returns a class
  which constructs objects which wrap the table for a particular object in the
  format returned by the GetManagedObjects() method of the ObjectManager
  interface. Each object has an instance method for each property of the
  interface.

* gmo_query_builder:
  This function consumes the spec for a single interface and returns a function
  which implements a query on the whole object returned by a GetManagedObjects()
  call. The query function takes two arguments: the GetManagedObjects() object
  and a dict of key/value pairs. The query function generates pairs of the
  object path and corresponding table which match all the key/value pairs in
  the table.

* dbus_python_invoker_builder:
  This functions consumes the spec for a single interface and returns a class
  that contains dbus-python dependent code to invoke methods on D-Bus objects.
  The client chooses the class name. Each generated class contains two static
  class members, "Methods" and "Properties". The "Methods" class has a number
  of static methods corresponding to every method defined in the interface.
  Each method takes a proxy object as its first argument followed by any
  number of keyword arguments, corresponding to the arguments of the method.
  The "Properties" class has a number of static classes corresponding to every
  property defined in the interface. Each property class has a static Get() or
  Set() method.

