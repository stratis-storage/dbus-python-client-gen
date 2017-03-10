# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Code for generating methods suitable for identifying objects in
the data structure returned by the GetManagedObjects() method.
"""

from ._errors import DPClientRuntimeError


def gmo_query_builder(spec):
    """
    Returns a function that builds a query method for an interface.
    This method encapsulates the locating of various managed objects
    according to the interface specifications.

    :param spec: the specification of an interface
    :type spec: Element
    """

    try:
        interface_name = spec.attrib['name']
    except KeyError as err: # pragma: no cover
        raise DPClientRuntimeError("No name for interface.") from err

    try:
        property_names = \
           frozenset(p.attrib['name'] for p in spec.findall("./property"))
    except KeyError as err: # pragma: no cover
        raise DPClientRuntimeError("No name for interface property.") from err

    def the_func(gmo, props=None):
        """
        Takes a list of key/value pairs representing properties
        and locates the corresponding objects which implement
        the designated interface for the spec.

        :param gmo: the result of a GetManagedObjects() call
        :param props: a specification of properties to restrict values
        :type props: dict of str * object or NoneType
        :returns: a list of pairs of object path/dict for the interface
        :rtype: list of tuple of ObjectPath * dict

        The function has conjunctive semantics, i.e., the object
        must match for every item in props to be returned.
        If props is None or an empty dict all objects that implement
        the designated interface are returned.

        :raises DPClientRuntimeError:
        """
        props = dict() if props is None else props

        if not frozenset(props.keys()) <= property_names:
            raise DPClientRuntimeError(
               "Unknown property for interface %s" % interface_name
            )

        for (op, data) in gmo.items():
            if not interface_name in data.keys():
                continue

            try:
                if all(data[interface_name][key] == value \
                        for (key, value) in props.items()):
                    yield (op, data)
            except KeyError as err:
                raise DPClientRuntimeError(
                   "Bad data for interface %s" % interface_name
                ) from err

    return the_func
