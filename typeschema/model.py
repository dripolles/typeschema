"""
typeschema.models defines useful classes that allow for declarative syntax
for objects with ``typeschema`` properties. A simple example looks like this.

>>> import typeschema.properties as ts

>>> class Example(Model):
...     foo = Property(ts.int, default=0)
...     bar = Property(ts.string)

Metaclass magic makes it possible to omit the name of the property. Instances of
``Example`` will have ``foo`` and ``bar`` properties, which will be instances of
``typeschema.int`` and ``typeschema.string`` respectively.

The ``Example`` class will also get a ``_meta`` attribute, instance of the ``Meta`` class
(see below). This class contains information about the way the model was declared.

"""

class Property(object):
    """
    Wraps a ``typeschema.property`` when using ``Model`` declarative syntax.
    All arguments and keyword arguments are used to instantiate the property.
    """
    def __init__(self, propclass, alias=None, *args, **kwargs):
        self.name = None # it will be set during metaclass __new__
        self.propclass = propclass
        self.alias = alias
        self.args = args
        self.kwargs = kwargs

    def get_property(self):
        if self.alias is None:
            raise RuntimeError('Unititialized alias for Property')

        return self.propclass(self.alias, *self.args, **self.kwargs)


class Meta(object):
    """
    Holds information about the definitions (``Property`` instances) and properties
    (``property`` instances) that belong to a ``Model``. Attributes:

    properties: a dict of name: property
    definitions: a dict of name: Property
    """
    def __init__(self):
        self.properties = {}
        self.definitions = {}


class ClassMeta(type):
    """
    Metaclass thas makes the declarative syntax possible. Replaces class-level
    instances of ``Property`` with instances of ``property``, and sets ``_meta`` to the proper
    ``Meta`` instance.
    """

    def __new__(cls, cls_name, bases, attrs):
        new_attrs = { '_meta': Meta() }

        for name, attr in attrs.items():
            if isinstance(attr, Property):
                attr.name = name
                if attr.alias is None:
                    attr.alias = attr.name
                cls._update_attrs_from_definition(new_attrs, attr)
            else:
                new_attrs[name] = attr

        return type.__new__(cls, cls_name, bases, new_attrs)

    @classmethod
    def _update_attrs_from_definition(cls, attrs, definition):
        property = definition.get_property()
        property.definition = definition
        attrs[definition.alias] = property
        meta = attrs['_meta']
        meta.properties[definition.name] = property
        meta.definitions[definition.name] = definition


class Class(object):
    """
    Base class for all classes that intend to use the declarative syntax for properties
    """
    __metaclass__ = ClassMeta

    @classmethod
    def definitions(cls):
        return dict(cls._meta.definitions)

    @classmethod
    def definition(cls, name):
        return cls._meta.definitions.get(name, None)

