# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Exception hierarchy for this package.
"""

# isort: STDLIB
from abc import ABC

# Put this pylint directive at module level. There's a slight bug in pylint
# that causes the directive to be ignored if there is no body to a class
# (because the pass statement is omitted). On the other hand, pylint now
# warns if it finds an unnecessary pass statement. This is the easiest course.


# pylint: disable=too-few-public-methods
class DPClientInvocationContext(ABC):
    """
    Identifies the context in which an invocation error occurred.

    The context can be a get property action, a set property action, or
    an actual method call. In each case, the fields of the subclass will
    be different.
    """


class DPClientMethodCallContext(DPClientInvocationContext):
    """
    Distinguishes a method call.
    """

    def __init__(self, method_name, method_args):  # pragma: no cover
        """
        Constructs method call information.

        :param str method_name: the method name
        :param method_args: the list of method arguments
        :type method_args: list of object
        """
        self.method_name = method_name
        self.method_args = method_args


class DPClientGetPropertyContext(DPClientInvocationContext):
    """
    Get call on a property.
    """

    def __init__(self, property_name):  # pragma: no cover
        """
        Construct property information.

        :param str property_name: the name of the property
        """
        self.property_name = property_name


class DPClientSetPropertyContext(DPClientInvocationContext):
    """
    Set call on a property.
    """

    def __init__(self, property_name, value):  # pragma: no cover
        """
        Construct property and value information.

        :param str property_name: the name of the property
        :param object value: the value to set
        """
        self.property_name = property_name
        self.value = value


class DPClientError(Exception):
    """
    Top-level error.
    """


class DPClientGenerationError(DPClientError):
    """
    Exception during generation of classes.
    """


class DPClientRuntimeError(DPClientError):
    """
    Exception raised during execution of generated classes.
    """

    def __init__(self, message, interface_name):
        """
        Initialize a DPClientRuntimeError with an interface name.
        All DPClientRuntimeErrors are guaranteed to have an interface name;
        the method has been constructed, so it must belong to some interface.

        :param str message: the error message
        :param str interface_name: the name of the interface
        """
        super().__init__(message)
        self.interface_name = interface_name


class DPClientInvocationError(DPClientRuntimeError):
    """
    Exception raised when dbus-python method call fails.
    """

    def __init__(self, message, interface_name, context):  # pragma: no cover
        """
        Initialize DPClientInvocationError

        :param str message: the message
        :param str interface_name: the interface name
        :param InvocationContext context: invocation context
        """
        super().__init__(message, interface_name)
        self.context = context


class DPClientInvalidArgError(DPClientRuntimeError):
    """
    Exception raised when an invalid argument is passed to a generated method.
    """


class DPClientMarshallingError(DPClientInvalidArgError):
    """
    Exception raised when the arguments could not be marshalled properly.
    """

    def __init__(
        self,
        message,
        interface_name,
        signature,
        arguments,
    ):
        """
        Initialize a DPClientMarshallingError with the arguments that failed.
        All DPClientMarshallingErrors are guaranteed to have a non-empty list
        of arguments.

        :param str message: the error message
        :param str interface_name: the name of the interface
        :param str signature: the D-Bus signature for the arguments
        :param arguments: list of object
        """
        super().__init__(message, interface_name)
        self.signature = signature
        self.arguments = arguments


class DPClientKeywordError(DPClientInvalidArgError):
    """
    Exception raised when keywords used do not match keywords expected.
    """

    def __init__(
        self,
        message,
        interface_name,
        method_name,
        expected,
        actual,
    ):  # pylint: disable=too-many-arguments, too-many-positional-arguments
        """
        Initialize a DPClientKeywordError with the mismatched arguments.

        :param str message: the error message
        :param str interface_name: the name of the interface
        :param str method_name: the name of the method invoked
        :param expected: the expected keywords
        :type expected: list of str
        :param actual: the actual keywords
        :type actual: list of str
        """
        super().__init__(message, interface_name)
        self.method_name = method_name
        self.expected = expected
        self.actual = actual
