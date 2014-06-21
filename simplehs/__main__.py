#!/usr/bin/env python
# Simple Hearthstone

import logging
import sys

from base import Match
from clients import ConsoleClient
from heroes import InnKeeper
from base import Deck
from cards import *

logging.basicConfig(level=logging.DEBUG)


def main(args=sys.argv[1:]):
    deck = Deck([
        MurlocRaider(),
        BloodfenRaptor(),
        RiverCrocolisk(),
        MagmaRager(),
        ChillwindYeti(),
        BoulderfistOgre(),
        CoreHound(),
        WarGolem(),
    ])
    client1 = ConsoleClient('Alice', InnKeeper, deck)
    client2 = ConsoleClient('Bob', InnKeeper, deck)
    match = Match(client1, client2)
    match.run()


if __name__ == '__main__':
    sys.exit(main())
