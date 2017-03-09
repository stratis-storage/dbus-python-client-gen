# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Code for generating classes suitable for invoking dbus-python methods.
"""

_IDENTITY = lambda x: x # pragma: no cover

def _option_to_tuple(value, default):
    """
    Converts a Python "option" type, None or a value, to a tuple.

    :param object value: any value
    :param object default: a valid default to use if value is None
    :returns: a tuple encoding the meaning of value
    :rtypes: bool * object
    """
    return (False, default) if value is None else (True, value)


def _info_to_xformer(specs):
    """
    Function that yields a xformer function.

    :param specs: specifications for this function
    :type names: iterable of triples, name, inxform function, sig
    :return: a transformation function
    :rtype: (list of object) -> (list of object)
    """
    inxforms = [y for (_, y, _) in specs]
    outxforms = [f for (f, _) in xformers("".join(z for (_, _, z) in specs))]
    expected_length = len(specs)

    def xformer(objects):
        """
        Transforms a list of objects to dbus-python types.

        :param objects: list of objects
        :type objects: list of object
        :returns: a transformed list of objects
        :rtype: list of object
        """
        if len(objects) != expected_length:
            raise ValueError("wrong number of objects")

        return \
           [x for (x, _) in (f(g(a)) for \
           ((f, g), a) in zip(zip(outxforms, inxforms), objects))]

    return xformer


def _xformers(key_to_sig):
    """
    Get a map from keys to functions from a map of names to signatures.

    :param key_to_sig: a map from keys to signatures
    :type key_to_sig: dict of object * str
    :returns: a map from keys to functions
    :rtype: dict of object * xformation function
    """
    return dict(
       (method, ([n for (n, _, _) in specs], _info_to_xformer(specs))) for \
       (method, specs) in key_to_sig.items())

def _prop_builder(spec):
    """
    Returns a function that builds a property interface based on 'spec'.

    :param spec: the interface specification
    :type spec: type, a subtype of InterfaceSpec
    """

    def builder(namespace):
        """
        The property class's namespace.

        :param namespace: the class's namespace
        """

        def build_property(prop): # pragma: no cover
            """
            Build a single property getter for this class.

            :param prop: the property
            """

            def dbus_func(proxy_object): # pragma: no cover
                """
                The property getter.
                """
                return proxy_object.Get(
                   spec.INTERFACE_NAME,
                   prop.name,
                   dbus_interface=dbus.PROPERTIES_IFACE
                )

            return dbus_func

        for prop in spec.PropertyNames:
            namespace[prop.name] = staticmethod(build_property(prop)) # pragma: no cover

    return builder


def _iface_builder(spec):
    """
    Returns a function that builds a method interface based on 'spec'.

    :param spec: the interface specification
    :type spec: type, a subtype of InterfaceSpec
    """

    def builder(namespace):
        """
        Builds the class.

        :param namespace: the class's namespace
        """

        def build_method(method):
            """
            Build a single method for this class.

            :param method: the method
            """
            (names, func) = spec.XFORMERS[method]

            def dbus_func(proxy_object, **kwargs): # pragma: no cover
                """
                The function method spec.
                """
                if frozenset(names) != frozenset(kwargs.keys()):
                    raise ValueError("Bad keys")
                args = \
                   [v for (k, v) in \
                   sorted(kwargs.items(), key=lambda x: names.index(x[0]))]
                xformed_args = func(args)
                dbus_method = getattr(proxy_object, method.name)
                return dbus_method(
                   *xformed_args,
                   dbus_interface=spec.INTERFACE_NAME
                )

            return dbus_func

        for method in spec.MethodNames:
            namespace[method.name] = staticmethod(build_method(method))

        namespace['Properties'] = \
           types.new_class(
              "Properties",
              bases=(object,),
              exec_body=_prop_builder(spec)
           )

    return builder
