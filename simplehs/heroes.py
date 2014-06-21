# Hero classes

from base import Hero


class InnKeeper(Hero):
    """An Inn Keeper hero (dummy)"""

    def __init__(self):
        Hero.__init__(self, 'Inn Keeper', 30)
