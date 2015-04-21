import unittest
from mock import Mock

import typeschema.properties as tp
from typeschema.model import Property, Meta, Class

class TestCase(unittest.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.definition_params = {
            'foo': (Mock(return_value=Mock()), (), {'default':0}),
            'bar': (Mock(return_value=Mock()), (), {}),
        }
        self.definitions = {
            'foo': self._get_define('foo'),
            'bar': self._get_define('bar'),
        }
        self.attrs = {
            'ignored': "ignored value"
        }

    def _get_define(self, name):
        prop, args, kwargs = self.definition_params[name]
        return Property(prop, *args, **kwargs)

    def test_model_meta_is_correct_instance(self):
        cls = self.get_example_class()
        self.assertIsInstance(cls._meta, Meta)

    def test_model_meta_has_correct_definitions(self):
        cls = self.get_example_class()
        definitions = cls._meta.definitions
        self.assertEqual(definitions, self.definitions)

    def test_model_meta_has_correct_properties(self):
        cls = self.get_example_class()
        for name, prop in cls._meta.properties.items():
            mock, args, kwargs = self.definition_params[name]
            self.assertEqual(prop, mock.return_value)
            mock.assert_called_once_with(name, *args, **kwargs)

    def get_example_class(self):
        class Example(Class):
            foo = self.definitions['foo']
            bar = self.definitions['bar']
            ignored = self.attrs['ignored']

        return Example

    def test_multiple_inheritance(self):
        class BaseOne(Class):
            foo = Property(Mock())

        class BaseTwo(Class):
            bar = Property(Mock())

        class Example(BaseOne, BaseTwo):
            pass

        self.assertEqual((Example.foo, Example.bar), (BaseOne.foo, BaseTwo.bar))

    def test_custom_alias(self):
        class Example(Class):
            foo = Property(Mock, alias='bar')

        self.assertIsInstance(Example.bar, Mock)
        self.assertIsNone(getattr(Example, 'foo', None))

    def test_custom_property(self):
        class Example(Class):
            foo = Property(tp.int, alias='_foo')

            @property
            def foo(self):
                return self._foo * 2

            @foo.setter
            def foo(self, value):
                self._foo = value * 2

        e = Example()
        e.foo = 2
        self.assertEqual((e.foo, e._foo), (8, 4))

    def test_custom_alias_keeps_original_name(self):
        class Example(Class):
            foo = Property(Mock, alias='bar')

        definition = Example.bar.definition
        self.assertEqual('foo', definition.name)
