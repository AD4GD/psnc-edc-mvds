## ****************************************************************************
## Niniejszy plik jest częścią pakietu programistycznego pytest-http.
## Wszelkie prawa do tego oprogramowania przysługują
## Instytutowi Chemii Bioorganicznej -
## Poznańskie Centrum Superkomputerowo-Sieciowe z siedzibą w Poznaniu.
## ****************************************************************************

from cached_property import cached_property

def assert_compatible_len(value):
    """This is to allow nice printing - builtin len() calls __index__ on the result __len__, thus losing context of WrappedProperty."""
    value = value.__len__()
    if isinstance(value, WrappedProperty):
        return value
    else:
        return value.__index__()


class WrappedProperty(object):

    def __init__(self, response, path, value):
        self.response = response
        self.path = path
        self.value = value

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __lt__(self, other):
        return self.value < other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __le__(self, other):
        return self.value <= other

    def __index__(self):
        return int(self.value)

    def __hash__(self):
        return hash(self.value)

    def __iter__(self):
        for i, item in enumerate(self.value):
            yield WrappedProperty(self.response, '%s[iter #%d]' % (self.path, i), item)

    def items(self):
        return self.value.items()

    def get(self, name, default=None):
        return self.value.get(name, default)

    def values(self):
        return map((lambda k: self[k]), self.value.keys())

    def __contains__(self, other):
        return other in self.value

    def __getitem__(self, name):
        try:
            return WrappedProperty(self.response, '%s[%r]' % (self.path, name), self.value[name])
        except KeyError:
            assert name in self
        except IndexError:
            assert assert_compatible_len(self) > name

    def __len__(self):
        return WrappedProperty(self.response, 'len(%s)' % (self.path), len(self.value))

    def __bool__(self):
        return bool(self.value)
        # return WrappedProperty(self.response, 'len(%s)' % (self.path), len(self.value))

    def __repr__(self):
        return self.path

    __str__ = __repr__


def wrapped_property(cached=False):

    def wrapper(func):
        name = func.__name__

        def wrapped(self):
            return WrappedProperty(self, path=('%r.%s' % (self, name)), value=func(self))

        return (cached_property if cached else property)(wrapped)

    return wrapper

