# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Code for generating classes suitable for invoking dbus-python methods.
"""
import types
import dbus

from into_dbus_python import IntoDPError
from into_dbus_python import xformer
from into_dbus_python import xformers

from ._errors import DPClientGenerationError
from ._errors import DPClientGetPropertyContext
from ._errors import DPClientInvocationError
from ._errors import DPClientKeywordError
from ._errors import DPClientMarshallingError
from ._errors import DPClientMethodCallContext
from ._errors import DPClientSetPropertyContext


def prop_builder(interface_name, properties, timeout):
    """
    Returns a function that builds a property interface based on arguments.

    Usage example:

    * spec is an xml specification for an interface in the format returned
    by the Introspect() method.
    * proxy_object is a dbus-python ProxyObject which implements
    the interface defined by spec which has a Name property.

    >>> builder = prop_builder("org.interface.inf", spec.findall("./property"), -1)
    >>> Properties = types.new_class("Properties", bases=(object,), exec_body=builder)
    >>> Properties.Name.Get(proxy_object)
    >>> Properties.Name.Set(proxy_object, "name")

    Note that both Get and Set are optional and depend on the properties of the
    attribute.

    :param str interface_name: the interface to which these properties belong
    :param properties: iterable of interface specifications for each property
    :type properties: iterable of xml.element.ElementTree.Element
    :param int timeout: the dbus method timeout, -1 is the libdbus default ~25s.

    :raises DPClientGenerationError:
    """

    def build_property_getter(name):
        """
        Build a single property getter for this class.

        :param str name: the name of the property
        """

        def dbus_func(proxy_object):  # pragma: no cover
            """
            The property getter.

            :raises DPClientInvocationError:
            """
            try:
                return proxy_object.Get(
                    interface_name,
                    name,
                    dbus_interface=dbus.PROPERTIES_IFACE,
                    timeout=timeout)
            except dbus.DBusException as err:
                err_msg = ("Error while getting value for property \"%s\" "
                           "belonging to interface \"%s\"") % (name,
                                                               interface_name)
                raise DPClientInvocationError(
                    err_msg, interface_name,
                    DPClientGetPropertyContext(name)) from err

        return dbus_func

    def build_property_setter(name, signature):
        """
        Build a single property setter for this class.

        :param str name: the name of the property
        :param str signature: the signature of the property
        """
        try:
            func = xformers(signature)[0]
        except IntoDPError as err:  #pragma: no cover
            fmt_str = (
                "Failed to generate argument-transforming function from "
                "signature \"%s\" for Set method for property \"%s\" "
                "belonging to interface \"%s\"")
            raise DPClientGenerationError(fmt_str % (signature, name,
                                                     interface_name)) from err

        def dbus_func(proxy_object, value):  # pragma: no cover
            """
            The property setter.

            :raises DPClientRuntimeError:
            """
            try:
                arg = func(value)
            except IntoDPError as err:
                err_msg = (
                    "Failed to format argument \"%s\" according to signature "
                    "\"%s\" for setter method for property \"%s\" belonging to "
                    "interface \"%s\"") % (value, signature, name,
                                           interface_name)
                raise DPClientMarshallingError(err_msg, interface_name,
                                               signature, [value]) from err

            try:
                return proxy_object.Set(
                    interface_name,
                    name,
                    arg,
                    dbus_interface=dbus.PROPERTIES_IFACE,
                    timeout=timeout)
            except dbus.DBusException as err:
                err_msg = ("Error while setting value of property \"%s\" "
                           "belonging to interface \"%s\" to value \"%s\"") % (
                               name, interface_name, arg)
                raise DPClientInvocationError(err_msg, interface_name,
                                              DPClientSetPropertyContext(
                                                  name, arg)) from err

        return dbus_func

    def build_property(access, name, signature):
        """
        Select among getter, setter, or both methods for a given property.

        :param str access: "read", "write", or "readwrite"
        :param str name: the name of the property
        :param str signature: the signature of the property

        :returns: a function which adds up to two methods to the namespace
        """
        if access == "read":
            getter = build_property_getter(name)

            def prop_method_builder(namespace):
                """
                Attaches getter to namespace.
                """
                namespace['Get'] = staticmethod(getter)

        elif access == "write":
            setter = build_property_setter(name, signature)

            def prop_method_builder(namespace):
                """
                Attaches setter to namespace
                """
                namespace['Set'] = staticmethod(setter)
        else:
            getter = build_property_getter(name)
            setter = build_property_setter(name, signature)

            def prop_method_builder(namespace):
                """
                Attaches getter and setter to namespace
                """
                namespace['Get'] = staticmethod(getter)
                namespace['Set'] = staticmethod(setter)

        return prop_method_builder

    def builder(namespace):
        """
        Fills the namespace of the parent class with class members that are
        classes. Each class member has the name of a property, and each
        class has up to two static methods, a Get method if the property is
        readable and a Set method if the property is writable.

        For example, given the spec:

        <property name="Version" type="s" access="read">
            <annotation
                name="org.freedesktop.DBus.Property.EmitsChangedSignal"
                value="const"/>
        </property>

        A class called "Version" with a single method "Get" will be added to the
        namespace.

        :param namespace: the class's namespace
        """
        for prop in properties:
            try:
                name = prop.attrib['name']
            except KeyError as err:  # pragma: no cover
                fmt_str = ("No name attribute found for property belonging to "
                           "interface \"%s\"")
                raise DPClientGenerationError(
                    fmt_str % interface_name) from err

            try:
                access = prop.attrib['access']
            except KeyError as err:  # pragma: no cover
                fmt_str = ("No access attribute found for property \"%s\" "
                           "belonging to interface \"%s\"")
                raise DPClientGenerationError(fmt_str %
                                              (name, interface_name)) from err
            try:
                signature = prop.attrib['type']
            except KeyError as err:  # pragma: no cover
                fmt_str = ("No type attribute found for property \"%s\" "
                           "belonging to interface \"%s\"")
                raise DPClientGenerationError(fmt_str %
                                              (name, interface_name)) from err

            namespace[name] = \
               types.new_class(
                   name,
                   bases=(object,),
                   exec_body=build_property(access, name, signature)
               )

    return builder


def method_builder(interface_name, methods, timeout):
    """
    Returns a function that builds a method interface based on 'spec'.

    Usage example:

    * spec is an xml specification for an interface in the format returned
    by the Introspect() method.
    * proxy_object is a dbus-python ProxyObject which implements
    the interface defined by spec which has a Name property.

    >>> builder = method_builder("org.interface.inf", spec.findall("./method"), -1)
    >>> Methods = types.new_class("Methods", bases=(object,), exec_body=builder)
    >>> Methods.Method(proxy_object)

    :param str interface_name: name the interface to which the methods belong
    :param methods: the iterable of interface specification for each method
    :type methods: iterator of xml.element.ElementTree.Element
    :param int timeout: the dbus method timeout, -1 is the libdbus default ~25s.

    :raises DPClientGenerationError:
    """

    def build_method(name, inargs):
        """
        Build a method for this class.

        :param str name: the name of the method
        :param inargs: the in-arguments to this methods
        :type inargs: iterable of Element
        """
        try:
            arg_names = [e.attrib["name"] for e in inargs]
        except KeyError as err:  # pragma: no cover
            fmt_str = ("No name attribute found for some argument for method "
                       "\"%s\" belonging to interface \"%s\"")
            raise DPClientGenerationError(fmt_str % (name,
                                                     interface_name)) from err

        try:
            signature = "".join(e.attrib["type"] for e in inargs)
        except KeyError as err:  #pragma: no cover
            fmt_str = ("No type attribute found for some argument for method "
                       "\"%s\" belonging to interface \"%s\"")
            raise DPClientGenerationError(fmt_str % (name,
                                                     interface_name)) from err

        try:
            func = xformer(signature)
        except IntoDPError as err:  #pragma: no cover
            fmt_str = ("Failed to generate argument-transforming function "
                       "from signature \"%s\" for method \"%s\" belonging to "
                       "interface \"%s\"")
            raise DPClientGenerationError(fmt_str % (signature, name,
                                                     interface_name)) from err
        arg_names_set = frozenset(arg_names)

        def dbus_func(proxy_object, func_args):  # pragma: no cover
            """
            The method proper.

            :param func_args: The function arguments
            :type func_args: dict
            :raises DPClientRuntimeError:
            """
            if arg_names_set != frozenset(func_args.keys()):
                param_list = [arg for arg in arg_names_set]
                arg_list = [arg for arg in func_args.keys()]
                err_msg = ("Argument keywords passed (%s) did not match "
                           "argument keywords expected (%s) for method \"%s\" "
                           "belonging to interface \"%s\"") % (
                               ", ".join(arg_list), ", ".join(param_list),
                               name, interface_name)
                raise DPClientKeywordError(err_msg, interface_name, name,
                                           arg_list, param_list)

            args = \
               [v for (k, v) in \
               sorted(func_args.items(), key=lambda x: arg_names.index(x[0]))]

            try:
                xformed_args = func(args)
            except IntoDPError as err:
                arg_str = ", ".join(str(arg) for arg in args)
                err_msg = ("Failed to format arguments (%s) according to "
                           "signature \"%s\" for method \"%s\" belonging to "
                           "interface \"%s\"") % (arg_str, signature, name,
                                                  interface_name)
                raise DPClientMarshallingError(err_msg, interface_name,
                                               signature, args) from err

            dbus_method = proxy_object.get_dbus_method(
                name, dbus_interface=interface_name)

            try:
                return dbus_method(*xformed_args, timeout=timeout)
            except dbus.DBusException as err:
                arg_str = ", ".join(str(arg) for arg in xformed_args)
                err_msg = ("Error while invoking method \"%s\" belonging to "
                           "interface \"%s\" with arguments (%s)") % (
                               name, interface_name, arg_str)
                raise DPClientInvocationError(err_msg, interface_name,
                                              DPClientMethodCallContext(
                                                  name, xformed_args)) from err

        return dbus_func

    def builder(namespace):
        """
        Fills the namespace of the parent class with class members that are
        methods. Each method takes a proxy object and a set of keyword
        arguments.

        For example, given the spec:

        <method name="CreatePool">
        <arg name="name" type="s" direction="in"/>
        <arg name="redundancy" type="(bq)" direction="in"/>
        <arg name="force" type="b" direction="in"/>
        <arg name="devices" type="as" direction="in"/>
        <arg name="result" type="(oas)" direction="out"/>
        <arg name="return_code" type="q" direction="out"/>
        <arg name="return_string" type="s" direction="out"/>
        </method>

        A method called "CreatePool" with four keyword arguments,
        "name", "redundancy", "force", "devices", will be added to the
        namespace.

        :param namespace: the class's namespace
        """
        for method in methods:
            try:
                name = method.attrib['name']
            except KeyError as err:  # pragma: no cover
                fmt_str = ("No name attribute found for method belonging to "
                           "interface \"%s\"")
                raise DPClientGenerationError(
                    fmt_str % interface_name) from err

            the_method = \
               build_method(name, method.findall('./arg[@direction="in"]'))
            namespace[name] = staticmethod(the_method)

    return builder


def make_class(name, spec, timeout=-1):
    """
    Make a class, name, from the given spec.
    The class defines static properties and methods according to the spec.

    :param str name: the name of the class.
    :param spec: the interface specification
    :type spec: xml.element.ElementTree.Element
    :param int timeout: dbus timeout for method(s), -1 is libdbus default ~25s.
    :returns: the constructed class
    :rtype: type
    """

    try:
        interface_name = spec.attrib['name']
    except KeyError as err:  # pragma: no cover
        raise DPClientGenerationError(
            "No name attribute found for interface") from err

    method_builder_arg = \
       method_builder(interface_name, spec.findall("./method"), timeout)
    prop_builder_arg = \
       prop_builder(interface_name, spec.findall("./property"), timeout)

    def builder(namespace):
        """
        Fills the namespace of the parent class with two class members,
        Properties and Methods. Both of these are classes which themselves
        contain static fields. Each static field in the Properties class
        is a class corresponding to a property of the interface. Each static
        field in the Methods class is a method corresponding to a method
        on the interface.

        :param namespace: the class's namespace
        """
        namespace["Methods"] = \
           types.new_class(
               "Methods",
               bases=(object,),
               exec_body=method_builder_arg
           )

        namespace["Properties"] = \
           types.new_class(
               "Properties",
               bases=(object,),
               exec_body=prop_builder_arg
           )

    return types.new_class(name, bases=(object, ), exec_body=builder)
