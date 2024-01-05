# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************
from __future__ import absolute_import

from .base import TypeScheme, TypedValue, empty, RawValue, List, Str
from .exceptions import ImproperlySpecifiedArguments, ImproperlyPassedArguments
from collections import OrderedDict
import sys
from .utils import append_to_dict, sort_ordered_dict
from six import with_metaclass


class GroupMetaclass(type):

    _counter = 0

    # _registry = {}

    def __new__(meta, name, bases, attributes):

        attributes['_counter'] = meta._counter
        static_arguments = OrderedDict()
        attributes['_static_arguments'] = static_arguments

        for attribute_name in list(attributes.keys()):
            if attribute_name.upper() == attribute_name:
                argument = TypeScheme.normalize(attributes[attribute_name])
                argument.attach_name(attribute_name)
                append_to_dict(static_arguments, argument.name, argument, 'argument')

        meta._counter += 1
        result = super(GroupMetaclass, meta).__new__(meta, name, bases, attributes)

        # meta._registry[name] = result

        return result

    # @classmethod
    # def explode_registry(meta, globals_dict):
    #     for k, v in meta._registry.items():
    #         globals_dict[k] = v


class Group(with_metaclass(GroupMetaclass, object)):

    @classmethod
    def get_group_class_name(cls):
        return cls.__name__.rstrip('Group').lower()

    def __init__(self, name=None, **arguments):
        self.name = name if name is not None else self.get_group_class_name()
        self._arguments = OrderedDict(self._static_arguments)
        # self._arguments = OrderedDict()

        for name, value in arguments.items():
            argument = TypeScheme.normalize(value)
            argument.attach_name(name)
            append_to_dict(self._arguments, name, argument, 'argument')

        self._arguments = sort_ordered_dict(self._arguments)


    @property
    def arguments(self):
        return self._arguments.values()





