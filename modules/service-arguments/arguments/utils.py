# coding=utf-8
## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego service-arguments.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************

from collections import OrderedDict
from .exceptions import ImproperlySpecifiedArguments
import functools

def append_to_dict(dictionary, name, value, description):
    if name in dictionary:
        raise ImproperlySpecifiedArguments('%s "%s" already specified' % (description, name))
    dictionary[name] = value

def sort_ordered_dict(dictionary):

    return OrderedDict(sorted(dictionary.items()))

def cached_property(func):
    name = '_%s' % func.__name__

    @property
    @functools.wraps(func)
    def wrapped(self):

        try:
            return getattr(self, name)
        except AttributeError:
            pass

        value = func(self)
        setattr(self, name, value)
        return value

    return wrapped
