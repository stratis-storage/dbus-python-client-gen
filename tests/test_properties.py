"""
Test generation of properties methods.
"""

import os
import types
import unittest

import xml.etree.ElementTree as ET

from dbus_python_client_gen._invokers import prop_builder


class PropertiesTestCase(unittest.TestCase):
    """
    Test that properties are appropriately generated.
    """

    _DIRNAME = os.path.dirname(__file__)

    def setUp(self):
        """
        Read introspection data.
        """
        self._data = dict()
        datadir = os.path.join(self._DIRNAME, "data")
        for name in os.listdir(datadir):
            if name[-4:] != '.xml':
                continue
            path = os.path.join(datadir, name)
            with open(path) as opath:
                self._data[name] = ET.fromstring("".join(opath.readlines()))

    def testGen(self):
        """
        Generate a klass from an interface spec and verify that it has
        the properties it should have.
        """
        for name, spec in self._data.items():
            builder = prop_builder(spec)
            klass = types.new_class(name, bases=(object,), exec_body=builder)
            for prop in spec.findall("./property"):
                name = prop.attrib['name']
                self.assertTrue(hasattr(klass, name))
                access = prop.attrib['access']
                prop_klass = getattr(klass, name)
                if "read" in access:
                    self.assertTrue(hasattr(prop_klass, "Get"))
                if "write" in access:
                    self.assertTrue(hasattr(prop_klass, "Set"))
