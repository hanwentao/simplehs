# Hero classes

from base import Hero


class InnKeeper(Hero):
    """An Inn Keeper hero (dummy)"""

    def __init__(self, root, id, owner):
        super(InnKeeper, self).__init__(root, id, owner, 'Inn Keeper', 30)
