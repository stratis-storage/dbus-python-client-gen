"""
Test generation of class for invoking dbus methods.
"""

import os
import types
import unittest

import xml.etree.ElementTree as ET

from dbus_python_client_gen import dbus_python_invoker_builder

from dbus_python_client_gen._invokers import method_builder
from dbus_python_client_gen._invokers import prop_builder



class TestCase(unittest.TestCase):
    """
    Test the behavior of various auto-generated classes
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

    def _test_property(self, klass, prop):
        """
        Test a single property.

        :param type klass: a class to which this property should belong
        :param prop: a specification of the property
        :type prop: Element
        """
        name = prop.attrib['name']
        self.assertTrue(hasattr(klass, name))
        access = prop.attrib['access']
        prop_klass = getattr(klass, name)
        if "read" in access:
            self.assertTrue(hasattr(prop_klass, "Get"))
        if "write" in access:
            self.assertTrue(hasattr(prop_klass, "Set"))

    def _testProperties(self):
        """
        Generate a klass from an interface spec and verify that it has
        the properties it should have.
        """
        for name, spec in self._data.items():
            builder = prop_builder(spec)
            klass = types.new_class(name, bases=(object,), exec_body=builder)
            for prop in spec.findall("./property"):
                self._test_property(klass, prop)

    def _test_method(self, klass, method):
        """
        Test a single method.

        :param type klass: a class to which this method should belong
        :param method: a specification of the method
        :type method: Element
        """
        name = method.attrib['name']
        self.assertTrue(hasattr(klass, name))

    def _testMethods(self):
        """
        Generate a class from an interface spec and verify that it has
        the properties it should have.
        """
        for name, spec in self._data.items():
            builder = method_builder(spec)
            klass = types.new_class(name, bases=(object,), exec_body=builder)
            for method in spec.findall("./method"):
                self._test_method(klass, method)

    def _testKlass(self):
        """
        Generate a class from an interface spec and verify that it has two
        fields, "Properties" and "Methods".
        """
        for name, spec in self._data.items():
            builder = dbus_python_invoker_builder(spec)
            klass = types.new_class(name, bases=(object,), exec_body=builder)
            self.assertTrue(hasattr(klass, "Properties"))
            properties = getattr(klass, "Properties")
            self.assertTrue(hasattr(klass, "Methods"))
            methods = getattr(klass, "Methods")
            for method in spec.findall("./method"):
                self._test_method(methods, method)

            for prop in spec.findall("./property"):
                self._test_property(properties, prop)

    def testSpecs(self):
        """
        Test properties and methods of all specs available.
        """
        self._testProperties()
        self._testMethods()
        self._testKlass()
