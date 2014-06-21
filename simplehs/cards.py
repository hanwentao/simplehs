# Card classes

from base import MinionCard
from base import SpellCard
from base import WeaponCard

# Neutral

# 0 mana

# 1 mana

class MurlocRaider(MinionCard):
    """Murloc Raider"""

    def __init__(self):
        MinionCard.__init__(self, 'Murloc Raider', 1, 2, 1)

# 2 mana

class BloodfenRaptor(MinionCard):
    """Bloodfen Raptor"""

    def __init__(self):
        MinionCard.__init__(self, 'Bloodfen Raptor', 2, 3, 2)


class RiverCrocolisk(MinionCard):
    """River Crocolisk"""

    def __init__(self):
        MinionCard.__init__(self, 'River Crocolisk', 2, 2, 3)

# 3 mana

class MagmaRager(MinionCard):
    """Magma Rager"""

    def __init__(self):
        MinionCard.__init__(self, 'Magma Rager', 3, 5, 1)

# 4 mana

class ChillwindYeti(MinionCard):
    """Chillwind Yeti"""

    def __init__(self):
        MinionCard.__init__(self, 'Chillwind Yeti', 4, 4, 5)

# 5 mana

# 6 mana

class BoulderfistOgre(MinionCard):
    """Boulderfist Ogre"""

    def __init__(self):
        MinionCard.__init__(self, 'Boulderfist Ogre', 6, 6, 7)

# 7+ mana

class CoreHound(MinionCard):
    """Core Hound"""

    def __init__(self):
        MinionCard.__init__(self, 'Core Hound', 7, 9, 5)


class WarGolem(MinionCard):
    """War Golem"""

    def __init__(self):
        MinionCard.__init__(self, 'War Golem', 7, 7, 7)
