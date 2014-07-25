#!/usr/bin/env python3
# Hero classes

from .base import Hero


class Innkeeper(Hero):
    """An Inn Keeper hero (dummy)"""

    def __init__(self, name='Innkeeper'):
        super().__init__(name, 30)


class Mage(Hero):
    """A Mage hero"""

    def __init__(self, name='Jaina Proudmoore'):
        super().__init__(name, 30)
