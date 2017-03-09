# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Code for generating classes suitable for invoking dbus-python methods.
"""
import types
import dbus

from ._errors import DPClientGenerationError


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
        The property class's namespace.

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
            # pylint: disable=cell-var-from-loop
            if name is None: # pragma: no cover
                raise DPClientGenerationError("No name found for property.")

            access = prop.attrib.get('access')
            if access is None: # pragma: no cover
                raise DPClientGenerationError("No access found for property.")

            if access == "read":
                getter = staticmethod(build_property_getter(name))

                def method_builder(namespace):
                    """
                    Attaches appropriate methods to namespace.
                    """
                    namespace['Get'] = getter

            elif access == "write":
                setter = staticmethod(build_property_setter(name))

                def method_builder(namespace):
                    """
                    Attaches appropriate methods to namespace.
                    """
                    namespace['Set'] = setter
            else:
                getter = staticmethod(build_property_getter(name))
                setter = staticmethod(build_property_setter(name))

                def method_builder(namespace):
                    """
                    Attaches appropriate methods to namespace.
                    """
                    namespace['Get'] = getter
                    namespace['Set'] = setter

            namespace[name] = \
               types.new_class(
                  name,
                  bases=(object,),
                  exec_body=method_builder
               )

    return builder
