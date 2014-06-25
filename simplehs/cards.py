# Card classes

from base import MinionCard
from base import SpellCard
from base import WeaponCard

_card_class_template = '''\
class {class_name}({base_class_name}):
    """{name}"""

    def __init__(self, root, id, owner):
        super({class_name}, self).__init__(root, id, owner, "{name}",
                                           {cost}, {attack}, {health})
'''

def _translate_name(name):
    class_name = ''
    first = True
    for ch in name:
        if ch.isalpha():
            if first:
                ch = ch.upper()
                first = False
            class_name += ch
        else:
            first = True
    return class_name

def make_card(base_class, name, cost, *args, **kwargs):
    arguments = dict(name=name, cost=cost)
    arguments['base_class_name'] = base_class.__name__
    class_name = _translate_name(name)
    arguments['class_name'] = class_name
    if base_class is MinionCard:
        arguments['attack'] = (kwargs['attack'] if 'attack' in kwargs
                                                else args[0])
        arguments['health'] = (kwargs['health'] if 'health' in kwargs
                                                else args[1])
    class_definition = _card_class_template.format(**arguments)
    namespace = dict(
        MinionCard=MinionCard,
        SpellCard=SpellCard,
        WeaponCard=WeaponCard,
    )
    exec class_definition in namespace
    card_class = namespace[class_name]
    return card_class

# Neutral

Wisp = make_card(MinionCard, 'Wisp', 0, 1, 1)
MurlocRaider = make_card(MinionCard, 'Murloc Raider', 1, 2, 1)
BloodfenRaptor = make_card(MinionCard, 'Bloodfen Raptor', 2, 3, 2)
RiverCrocolisk = make_card(MinionCard, 'River Crocolisk', 2, 2, 3)
MagmaRager = make_card(MinionCard, 'Magma Rager', 3, 5, 1)
ChillwindYeti = make_card(MinionCard, 'Chillwind Yeti', 4, 4, 5)
BoulderfistOgre = make_card(MinionCard, 'Boulderfist Ogre', 6, 6, 7)
CoreHound = make_card(MinionCard, 'Core Hound', 7, 9, 5)
WarGolem = make_card(MinionCard, 'War Golem', 7, 7, 7)

# Special

class TheCoin(SpellCard):
    """The Coin"""

    def __init__(self, root, id, owner):
        super(TheCoin, self).__init__(root, id, owner, 'The Coin', 0)

    def play(self):
        SpellCard.play(self)
        self.owner._mana += 1
