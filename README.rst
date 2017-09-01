A Python Library for Generating dbus-python Client Code
=======================================================

Introduction
------------
This library contains a method that consumes an XML specification of
a D-Bus interface and yields a Pythonic interface for invoking methods and
obtaining properties on that interface using the dbus-python library.

Methods
-------

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
