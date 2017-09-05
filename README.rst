A Python Library for Generating dbus-python Client Code
=======================================================

Function
--------
This library contains a function, make_class, that consumes
an XML specification of a D-Bus interface. ::

>>> Klass = make_class("Klass", spec)

This call yields a Python class, called Klass, with two static class
members, "Methods" and "Properties". The "Methods" class has a static
method corresponding to each method defined in the interface. Each method
takes a proxy object as its first argument followed by any number of
keyword arguments, corresponding to the arguments of the method. The
"Properties" class has a static class corresponding to every property
defined in the interface. Each property class may have a static Get() or
Set() method, depending on its attributes.

For example, assuming the interface defines a read only Version property,
the following call should return a value. ::

>>> Klass.Properties.Version.Get()

However, since Version is a read only property, the following call should
fail with an AttributeError. ::

>>> Klass.Properties.Version.Set("42")

Similarly, if the interface defines a method, Create, with one argument,
name, a STRING, the following call should succeed. ::

>>> Klass.Methods.Create(proxy, name="name")

The Create method invokes the method on the proxy object, passing force,
transformed into a dbus-python String type.

On the other hand, the invocation will raise a DPClientError exception if
the method is called with an argument with an incorrect type as, ::

>>> Klass.Methods.Create(proxy, name=false)

or with an incorrect keyword as, ::

>>> Klass.Methods.Create(proxy, force=false)

or without all the necessary keywords as, ::

>>> Klass.Methods.Create(proxy)

Errors
------
This library exports one exception type, DPClientError. It constitutes a bug
if an error of any other type is propagated during class generation or when
the methods of the class are executed.

Dependencies
------------
* dbus-python
* into-dbus-python

Requirements
------------
This library is not compatible with Python 2.
