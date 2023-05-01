"""
Test generation of class for invoking dbus methods.
"""

# isort: STDLIB
import unittest
import xml.etree.ElementTree as ET

# isort: FIRSTPARTY
from tests._introspect import SPECS

# isort: LOCAL
from dbus_python_client_gen import (
    DPClientGenerationError,
    DPClientKeywordError,
    DPClientMarshallingError,
    make_class,
)

try:
    interfaces = list(SPECS)

    TIMEOUT = 120000

    klasses = {}
    for key, value in SPECS.items():
        xml_spec = ET.fromstring(value)
        klass_def = make_class(key.split(".")[-2], xml_spec, TIMEOUT)
        klasses[key] = (xml_spec, klass_def)

except DPClientGenerationError as err:
    raise RuntimeError(
        "Failed to generate some class needed for invoking dbus-python methods"
    ) from err


class TestCase(unittest.TestCase):
    """
    Test the behavior of various auto-generated classes
    """

    def _test_property(self, klass, prop):
        """
        Test a single property.

        :param type klass: a class to which this property should belong
        :param prop: a specification of the property
        :type prop: Element
        """
        name = prop.attrib["name"]
        self.assertTrue(hasattr(klass, name))
        access = prop.attrib["access"]
        prop_klass = getattr(klass, name)
        if "read" in access:
            self.assertTrue(hasattr(prop_klass, "Get"))

            with self.assertRaises(AttributeError):
                getattr(prop_klass, "Get")(None)

        if "write" in access:
            self.assertTrue(hasattr(prop_klass, "Set"))

            if name == "Overprovisioning":
                # Overprovisioning takes a boolean argument and almost
                # every Python object can be interpreted as a boolean.
                # Could be considered to be a minor bug in into-dbus-python.
                pass
            else:
                with self.assertRaises(DPClientMarshallingError):
                    getattr(prop_klass, "Set")(None, None)

        if "readwrite" in access:
            self.assertTrue(hasattr(prop_klass, "Get"))
            self.assertTrue(hasattr(prop_klass, "Set"))

            with self.assertRaises(AttributeError):
                getattr(prop_klass, "Get")(None)

    def _test_method(self, klass, method):
        """
        Test a single method.

        :param type klass: a class to which this method should belong
        :param method: a specification of the method
        :type method: Element
        """
        name = method.attrib["name"]
        self.assertTrue(hasattr(klass, name))

        method = getattr(klass, name)
        with self.assertRaises(DPClientKeywordError):
            method(None, {"bogus_keyword": None})

    def _test_klasses(self):
        """
        Test the standard classes specified.
        """
        for (_, (spec, klass)) in klasses.items():
            self.assertTrue(hasattr(klass, "Properties"))
            self.assertTrue(hasattr(klass, "Methods"))

            properties = getattr(klass, "Properties")
            methods = getattr(klass, "Methods")

            for method in spec.findall("./method"):
                self._test_method(methods, method)

            for prop in spec.findall("./property"):
                self._test_property(properties, prop)

    def test_specs(self):
        """
        Test properties and methods of all specs available.
        """
        self._test_klasses()
