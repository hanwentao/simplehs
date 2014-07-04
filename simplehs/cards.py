# Card classes

from base import MinionCard
from base import SpellCard
from base import WeaponCard

_card_class_template = '''\
class {class_name}({base_class_name}):
    """{name}"""

    def __init__(self, root, id, owner):
        super({class_name}, self).__init__(root, id, owner, "{name}", {cost},
                                           **{kwargs_repr})
'''

def generate_class_name(name):
    """Generate class name from a literate name.

    >>> generate_class_name("Murloc Raider")
    'MurlocRaider'
    >>> generate_class_name("Kor'kron Elite")
    'KorkronElite'
    >>> generate_class_name("Al'Akir the Windlord")
    'AlAkirTheWindlord'
    >>> generate_class_name("Power Word: Shield")
    'PowerWordShield'
    """

    class_name = ''
    first = True
    for ch in name:
        if ch.isalpha():
            if first:
                ch = ch.upper()
                first = False
            class_name += ch
        elif ch.isspace():
            first = True
    return class_name

def make_card(base_class, name, cost, *args, **kwargs):
    arguments = dict(name=name, cost=cost)
    arguments['base_class_name'] = base_class.__name__
    class_name = generate_class_name(name)
    arguments['class_name'] = class_name
    if base_class is MinionCard and len(args) == 2:
        kwargs['attack'] = args[0]
        kwargs['health'] = args[1]
    arguments['kwargs_repr'] = repr(kwargs)
    class_definition = _card_class_template.format(**arguments)
    namespace = dict(
        MinionCard=MinionCard,
        SpellCard=SpellCard,
        WeaponCard=WeaponCard,
    )
    exec class_definition in namespace
    card_class = namespace[class_name]
    return card_class

# Vanilla

Wisp = make_card(MinionCard, "Wisp", 0, 1, 1)
MurlocRaider = make_card(MinionCard, "Murloc Raider", 1, 2, 1)
BloodfenRaptor = make_card(MinionCard, "Bloodfen Raptor", 2, 3, 2)
RiverCrocolisk = make_card(MinionCard, "River Crocolisk", 2, 2, 3)
MagmaRager = make_card(MinionCard, "Magma Rager", 3, 5, 1)
ChillwindYeti = make_card(MinionCard, "Chillwind Yeti", 4, 4, 5)
BoulderfistOgre = make_card(MinionCard, "Boulderfist Ogre", 6, 6, 7)
CoreHound = make_card(MinionCard, "Core Hound", 7, 9, 5)
WarGolem = make_card(MinionCard, "War Golem", 7, 7, 7)

# Charge

StonetuskBoar = make_card(MinionCard, "Stonetusk Boar", 1, 1, 1, charge=True)
BluegillWarrior = make_card(MinionCard, "Bluegill Warrior", 2, 2, 1, charge=True)
Wolfrider = make_card(MinionCard, "Wolfrider", 3, 3, 1, charge=True)
KorkronElite = make_card(MinionCard, "Kor'kron Elite", 4, 4, 3, charge=True)
StormwindKnight = make_card(MinionCard, "Stormwind Knight", 4, 2, 5, charge=True)
RecklessRocketeer = make_card(MinionCard, "Reckless Rocketeer", 6, 5, 2, charge=True)
KingKrush = make_card(MinionCard, "King Krush", 9, 8, 8, charge=True)

# Taunt

GoldshireFootman = make_card(MinionCard, "Goldshire Footman", 1, 1, 2, taunt=True)
Shieldbearer = make_card(MinionCard, "Shieldbearer", 1, 0, 4, taunt=True)
Voidwalker = make_card(MinionCard, "Voidwalker", 1, 1, 3, taunt=True)
FrostwolfGrunt = make_card(MinionCard, "Frostwolf Grunt", 2, 2, 2, taunt=True)
IronfurGrizzly = make_card(MinionCard, "Ironfur Grizzly", 3, 3, 3, taunt=True)
SilverbackPatriarch = make_card(MinionCard, "Silverback Patriarch", 3, 1, 4, taunt=True)
MogushanWarden = make_card(MinionCard, "Mogu'shan Warden", 4, 1, 7, taunt=True)
SenjinShieldmasta = make_card(MinionCard, "Sen'jin Shieldmasta", 4, 3, 5, taunt=True)
BootyBayBodyguard = make_card(MinionCard, "Booty Bay Bodyguard", 5, 5, 4, taunt=True)
FenCreeper = make_card(MinionCard, "Fen Creeper", 5, 3, 6, taunt=True)
LordOfTheArena = make_card(MinionCard, "Lord of the Arena", 6, 6, 5, taunt=True)
IronbarkProtector = make_card(MinionCard, "Ironbark Protector", 8, 8, 8, taunt=True)

# Special

class TheCoin(SpellCard):
    """The Coin"""

    def __init__(self, root, id, owner):
        super(TheCoin, self).__init__(root, id, owner, 'The Coin', 0)

    def play(self):
        SpellCard.play(self)
        self.owner._mana += 1


if __name__ == '__main__':
    import doctest
    doctest.testmod()
