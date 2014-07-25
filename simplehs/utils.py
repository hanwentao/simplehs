#!/usr/bin/env python3

import importlib


class Dict(dict):
    """A dictionary that can use attribute as key.

    >>> d = Dict(x=1)
    >>> d
    {'x': 1}
    >>> d.y = 2
    >>> del d.x
    >>> d
    {'y': 2}
    """

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def copy(self):
        return Dict(self)


class List(list):
    """A list which has a recursive __str__.

    >>> l = List([1, 'x'])
    >>> str(l)
    '[1, x]'
    """

    def __str__(self):
        return '[' + ', '.join(str(item) for item in self) + ']'

    @property
    def size(self):
        return len(self)


class Random:
    """A dummy pseudo-random generator like random.Random."""

    def randrange(self, start_or_stop, stop=None, step=1):
        if stop is None:
            start = 0
            stop = start_or_stop
        else:
            start = start_or_stop
        return start

    def choice(self, iterable):
        index = self.randrange(len(iterable))
        return iterable[index]

    def shuffle(self, iterable):
        return iterable


def get_class(class_):
    """Return the class from a class or its name."""
    if isinstance(class_, type):
        return class_
    if isinstance(class_, str):
        # TODO: Resolve the class name
        module = importlib.import_module('.base', 'simplehs')
        namespace = module.__dict__
        if class_ in namespace:
            return namespace[class_]
    raise ValueError('unknown class')


def join_args(args):
    return ', '.join(k + '=' + str(v) for k, v in args.items())


def pascalize(name):
    """Return the Pascal form of the given name.

    All non-letter characters will be removed, and each word will be
    capitalized.

    >>> pascalize("Murloc Raider")
    'MurlocRaider'
    >>> pascalize("Kor'kron Elite")
    'KorkronElite'
    >>> pascalize("Al'Akir the Windlord")
    'AlAkirTheWindlord'
    >>> pascalize("Power Word: Shield")
    'PowerWordShield'
    >>> pascalize("Alarm-o-Bot")
    'AlarmOBot'
    """

    class_name = ''
    first = True
    for ch in name:
        if ch.isalpha():
            if first:
                ch = ch.upper()
                first = False
            class_name += ch
        elif ch.isspace() or ch == '-':
            first = True
    return class_name


def to_number(number):
    """Convert an English word to a number.

    >>> to_number('a')
    1
    >>> to_number('an')
    1
    >>> to_number('one')
    1
    >>> to_number('two')
    2
    >>> to_number('three')
    3
    >>> to_number('four')
    Traceback (most recent call last):
        ...
    ValueError: unknown number
    """

    if number == 'a' or number == 'an' or number == 'one':
        return 1
    elif number == 'two':
        return 2
    elif number == 'three':
        return 3
    else:
        raise ValueError('unknown number')


if __name__ == '__main__':
    import doctest
    doctest.testmod()
