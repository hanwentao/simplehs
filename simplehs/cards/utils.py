#!/usr/bin/env python3

from ..utils import get_class
from ..utils import join_args
from ..utils import pascalize
from ..base import MinionCard
from ..base import SpellCard
from ..base import WeaponCard
from ..actions import *

__all__ = [
    'make_minion_card',
    'make_spell_card',
    'make_weapon_card',
]


_MINION_CARD_CLASS_TEMPLATE = """\
class {class_name}(MinionCard):

    def __init__(self):
        super().__init__("{name}", {cost}, {attack}, {health}{abilities})
"""

def make_minion_card(name, cost, attack, health, **kwargs):
    class_name = pascalize(name)
    abilities = ', ' + join_args(kwargs)
    class_definition = _MINION_CARD_CLASS_TEMPLATE.format(**locals())
    namespace = dict(globals())
    exec(class_definition, namespace)
    class_ = namespace[class_name]
    return class_


def make_spell_card(name, cost, **kwargs):
    pass


def make_weapon_card(name, cost, attack, durability, **kwargs):
    pass
