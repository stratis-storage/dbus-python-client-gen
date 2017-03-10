# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Code for generating classes suitable for invoking dbus-python methods.
"""
import types
import dbus

from into_dbus_python import xformers

from ._errors import DPClientGenerationError
from ._errors import DPClientRuntimeError


def prop_builder(spec):
    """
    Returns a function that builds a property interface based on 'spec'.

    :param spec: the interface specification
    :type spec: xml.element.ElementTree.Element

    :raises DPClientGenerationError:
    """

    interface_name = spec.attrib.get('name')
    if interface_name is None: # pragma: no cover
        raise DPClientGenerationError("No name found for interface.")

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

        def build_property_getter(name):
            """
            Build a single property getter for this class.

            :param str name: the property name
            """

            def dbus_func(proxy_object): # pragma: no cover
                """
                The property getter.
                """
                return proxy_object.Get(
                   interface_name,
                   name,
                   dbus_interface=dbus.PROPERTIES_IFACE
                )

            return dbus_func

        def build_property_setter(name):
            """
            Build a single property setter for this class.

            :param str name: the property name
            """

            def dbus_func(proxy_object, value): # pragma: no cover
                """
                The property setter.
                """
                return proxy_object.Set(
                   interface_name,
                   name,
                   value,
                   dbus_interface=dbus.PROPERTIES_IFACE
                )

            return dbus_func

        for prop in spec.findall('./property'):
            name = prop.attrib.get('name')
            if name is None: # pragma: no cover
                raise DPClientGenerationError("No name found for property.")

            access = prop.attrib.get('access')
            if access is None: # pragma: no cover
                raise DPClientGenerationError("No access found for property.")

            if access == "read":
                getter = build_property_getter(name)

                def prop_method_builder(namespace):
                    """
                    Attaches appropriate methods to namespace.
                    """
                    # pylint: disable=cell-var-from-loop
                    namespace['Get'] = staticmethod(getter)

            elif access == "write":
                setter = build_property_setter(name)

                def prop_method_builder(namespace):
                    """
                    Attaches appropriate methods to namespace.
                    """
                    # pylint: disable=cell-var-from-loop
                    namespace['Set'] = staticmethod(setter)
            else:
                getter = build_property_getter(name)
                setter = build_property_setter(name)

                def prop_method_builder(namespace):
                    """
                    Attaches appropriate methods to namespace.
                    """
                    # pylint: disable=cell-var-from-loop
                    namespace['Get'] = staticmethod(getter)
                    namespace['Set'] = staticmethod(setter)

            namespace[name] = \
               types.new_class(
                  name,
                  bases=(object,),
                  exec_body=prop_method_builder
               )

    return builder


def method_builder(spec):
    """
    Returns a function that builds a method interface based on 'spec'.

    :param spec: the interface specification
    :type spec: xml.element.ElementTree.Element

    :raises DPClientGenerationError:
    """

    interface_name = spec.attrib.get('name')
    if interface_name is None: # pragma: no cover
        raise DPClientGenerationError("No name found for interface.")

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

        def build_method(spec):
            """
            Build a method for this class.

            :param spec: the specification for a single method
            :type spec: Element
            """

            name = spec.attrib.get("name")
            if name is None: # pragma: no cover
                raise DPClientGenerationError("No name found for method.")

            inargs = spec.findall('./arg[@direction="in"]')
            arg_names = [e.attrib["name"] for e in inargs]

            signature = "".join(e.attrib["type"] for e in inargs)
            func = xformers(signature)

            def dbus_func(proxy_object, **kwargs): # pragma: no cover
                """
                The method proper.
                """
                if frozenset(arg_names) != frozenset(kwargs.keys()):
                    raise DPClientRuntimeError("Key mismatch: %s != %s" %
                       (", ".join(arg_names), ", ".join(kwargs.keys())))
                args = \
                   [v for (k, v) in \
                   sorted(kwargs.items(), key=lambda x: arg_names.index(x[0]))]
                xformed_args = func(args)
                dbus_method = getattr(proxy_object, name)
                return dbus_method(*xformed_args, dbus_interface=interface_name)

            return dbus_func

        for method in spec.findall('./method'):
            name = method.attrib.get('name')
            if name is None: # pragma: no cover
                raise DPClientGenerationError("No name found for method.")

            namespace[name] = staticmethod(build_method(method))

    return builder


def class_builder(spec):
    """
    Returns a function that builds a method interface based on 'spec'.

    :param spec: the interface specification
    :type spec: xml.element.ElementTree.Element

    :raises DPClientGenerationError:
    """

    interface_name = spec.attrib.get('name')
    if interface_name is None: # pragma: no cover
        raise DPClientGenerationError("No name found for interface.")

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
              exec_body=method_builder(spec)
           )

        namespace["Properties"] = \
           types.new_class(
              "Properties",
              bases=(object,),
              exec_body=prop_builder(spec)
           )

    return builder
