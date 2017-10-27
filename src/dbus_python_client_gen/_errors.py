# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Exception hierarchy for this package.
"""

class DPClientError(Exception):
    """
    Top-level error.
    """
    pass

class DPClientGenerationError(DPClientError):
    """
    Exception during generation of classes.
    """
    pass

class DPClientRuntimeError(DPClientError):
    """
    Exception raised during execution of generated classes.
    """
    pass

class DPClientInvocationError(DPClientRuntimeError):
    """
    Exception raised when dbus-python method call fails.
    """
    pass

class DPClientInvalidArgError(DPClientRuntimeError):
    """
    Exception raised when an invalid argument is passed to a generated method.
    """
    pass
