# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import absolute_import

from six import with_metaclass
from path import Path as PyPath
import json
import base64
from .exceptions import ImproperlySpecifiedArguments, ImproperlyPassedArguments


class EmptyValue(object):

    def __str__(self):
        return '<empty>'

    def __repr__(self):
        return '<empty>'

    def __nonzero__(self):
        return False

empty = EmptyValue()

class RawValue(object):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return 'raw(%r)' % self.value

class TypedValue(object):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return 'typed(%r)' % self.value

class RefValue(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '$%s' % self.name

    def __repr__(self):
        return 'ref(%r)' % self.name

Ref = RefValue

class Result(object):

    def __init__(self, output_value, input_value=None, origin=None, intermediate_value=None):
        self.output_value = output_value
        self.input_value = input_value
        self.origin = origin
        self.intermediate_value = intermediate_value

    @classmethod
    def wrap(cls, value):

        if isinstance(value, cls):
            return value

        return cls(output_value=value)


class TypeSchemeMetaclass(type):

    _registry = {}

    def __new__(meta, name, bases, attributes):

        result = super(TypeSchemeMetaclass, meta).__new__(meta, name, bases, attributes)
        meta._registry[name] = result

        return result

    @classmethod
    def explode_registry(meta, globals_dict):
        for k, v in meta._registry.items():
            globals_dict[k] = v

class TypeScheme(with_metaclass(TypeSchemeMetaclass, object)):

    def __init__(self, default=empty, name=None, encoding=None):
        if isinstance(default, TypedValue):
            self.default = default
        elif isinstance(default, RawValue):
            self.default = default
        elif isinstance(default, RefValue):
            self.default = default
        elif default is empty:
            self.default = empty
        elif default is None:
            self.default = None
        elif isinstance(default, str):
            self.default = RawValue(default)
        else:
            self.default = TypedValue(default)
        # TODO : add support for empty list and empty dict
        # else:
        #     assert False, 'default value passed is of unknown type "%s"' % type(default)

        self.name = name
        assert encoding in ('base64', None)
        self.encoding = encoding

    def attach_name(self, name):
        assert self.name is None
        self.name = name

    def has_default(self):
        return self.default is not empty


    def get_default_result(self, provider=None):
        if not self.has_default():
            # error_msg = "Set the {0} environment variable".format(var)
            raise ImproperlyPassedArguments('%s has no default value, and no value was specified' % self.name)

        if isinstance(self.default, TypedValue):
            return Result.wrap(self.default.value)
        elif self.default is None:
            return Result.wrap(None)
        elif isinstance(self.default, RawValue):
            return self.parse_into_result(self.default.value)
        elif isinstance(self.default, RefValue):
            assert provider is not None
            return provider.get_result(self.default.name)
            # return self.parse(self.default.value)
        else:
            raise Exception('invalid default')

    def get_default(self, provider=None):
        return self.get_default_result(provider=provider).output_value

    @classmethod
    def normalize(cls, spec):

        if spec is None:
            return Str()

        if isinstance(spec, TypeScheme):
            return spec

        PRIMITIVE_TYPES = (int, float, str)
        if spec in PRIMITIVE_TYPES:
            return PRIMITIVE_SCHEMES[spec](default=empty)
        if isinstance(spec, PRIMITIVE_TYPES):
            return PRIMITIVE_SCHEMES[type(spec)](default=TypedValue(spec))

        # TODO : or maybe here

        if isinstance(spec, list):
            spec_length = len(spec)
            if spec_length == 1:
                element_scheme = cls.normalize(spec[0])
                if element_scheme.default is empty:
                    default = TypedValue([])
                else:
                    default = TypedValue([element_scheme.get_default()])
            elif spec_length == 0:
                element_scheme = Str()
                default = TypedValue([])
            else:
                element_scheme = None
                default_elements = []
                for s in spec:
                    scheme = cls.normalize(s)

                    if element_scheme is not None:
                        assert type(element_scheme) == type(scheme)
                    else:
                        element_scheme = scheme
                    assert scheme.default is not empty, "empty default value of multiple list"
                    default_elements.append(scheme.get_default())

                default = TypedValue(default_elements)

            return List(element_scheme=element_scheme, default=default)

        if isinstance(spec, type):
            if issubclass(spec, TypeScheme):
                return spec(default=empty)
            raise ImproperlySpecifiedArguments('invalid schema type: %r' % spec)

        if isinstance(spec, tuple):
            element_schemes = []
            default = []

            for element_spec in spec:
                element_scheme = cls.normalize(element_spec)
                element_schemes.append(element_scheme)
                if element_scheme.default is not empty:
                    default.append(element_scheme.get_default())

            if len(default) != len(spec):
                raise ImproperlySpecifiedArguments('either all tuple elements must have default value or none of them')

            return Tuple(tuple(element_schemes), default=tuple(default))

        raise ImproperlySpecifiedArguments('invalid schema: %r' % spec)

    def parse(self, value, provider=None):
        return self.parse_into_result(value, provider).output_value

    def parse_into_result(self, value, provider=None):
        if self.encoding == 'base64':
            value = base64.b64decode(value)
            if isinstance(value, bytes):
                value = value.decode('utf-8')
        return Result.wrap(self._parse_decoded(value, provider=provider))

    def _parse_decoded(self, value, provider):
        raise NotImplementedError('_parse_decoded in %s' % self.__class__.__name__)


    @classmethod
    def normalize_and_parse(cls, spec, value):
        scheme = cls.normalize(spec)
        return scheme.parse(value)


class Primitive(TypeScheme):

    def _parse_decoded(self, value, provider):
        try:
            return self.primitive_type(value)
        except ValueError as e:
            raise ImproperlyPassedArguments('%r is not a proper %s type: %s' % (value, self.primitive_type, str(e)))

class Int(Primitive):
    primitive_type = int

class Str(Primitive):
    primitive_type = str

class Float(Primitive):
    primitive_type = float


class Bool(Primitive):
    primitive_type = bool

    TRUE_STRINGS = ('true', 'on', 'ok', 'y', 'yes', '1')
    FALSE_STRINGS = ('false', 'off', 'n', 'no', '0')

    def _parse_decoded(self, value, provider):
        lower_value = value.lower()
        if lower_value in self.TRUE_STRINGS:
            return True
        if lower_value in self.FALSE_STRINGS:
            return False
        raise ImproperlyPassedArguments('invalid boolean value: "%s"' % value)


class Path(TypeScheme):

    def _parse_decoded(self, value, provider):
        return PyPath(value)


class Tuple(TypeScheme):

    def __init__(self, element_schemes, **kwargs):
        super(Tuple, self).__init__(**kwargs)
        assert isinstance(element_schemes, tuple), "%s is not a TypeScheme instance" % element_scheme
        assert len(element_schemes) > 0
        for e in element_schemes:
            assert isinstance(e, TypeScheme)
        self.element_schemes = element_schemes

    def _parse_decoded(self, value, provider):
        elements = value.split(',')
        if len(elements) != len(self.element_schemes):
            raise ImproperlyPassedArguments('invalid length of tuple: should be %d but %d given' % (len(self.element_schemes), len(elements)))
        return tuple([scheme.parse(element) for element, scheme in zip(elements, self.element_schemes)])



class List(TypeScheme):

    def __init__(self, element_scheme, **kwargs):
        super(List, self).__init__(**kwargs)
        assert isinstance(element_scheme, TypeScheme), "%s is not a TypeScheme instance" % element_scheme
        self.element_scheme = element_scheme

    def _parse_decoded(self, value, provider):
        if value == '':
            return []
        elements = value.split(',')
        return list(map(self.element_scheme.parse, elements))


class Dict(TypeScheme):

    def __init__(self, key=None, value=None, **kwargs):
        super(Dict, self).__init__(**kwargs)
        self.key_scheme = TypeScheme.normalize(key)
        self.value_scheme = TypeScheme.normalize(value)

    def _parse_decoded(self, value, provider):
        items = value.split(',')
        result = {}
        for item in items:
            key_source, value_source = item.split(':', 1)
            item_key = self.key_scheme.parse(key_source)
            item_value = self.value_scheme.parse(value_source)
            result[item_key] = item_value

        return result


class Json(TypeScheme):

    def _parse_decoded(self, value, provider):
        return json.loads(value)


PRIMITIVE_SCHEMES = { s.primitive_type: s for s in [ Int, Str, Float, Bool ] }


