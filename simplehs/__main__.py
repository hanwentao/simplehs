#!/usr/bin/env python
# Simple Hearthstone

import logging
import sys

from base import Deck
from base import Match
from cards import *
from clients import *
from heroes import *

logging.basicConfig(level=logging.DEBUG)


def main(args=sys.argv[1:]):
    seed = 1 if not args else args[0]
    deck = Deck(
        [MurlocRaider()] * 9 +
        [BloodfenRaptor()] * 5 +
        [RiverCrocolisk()] * 5 +
        [MagmaRager()] * 4 +
        [ChillwindYeti()] * 3 +
        [BoulderfistOgre()] * 2 +
        [CoreHound()] * 1 +
        [WarGolem()] * 1 +
        [])
    client1 = NaiveClient('Alice', InnKeeper, deck)
    client2 = NaiveClient('Bob', InnKeeper, deck)
    match = Match(client1, client2, seed)
    match.run()


if __name__ == '__main__':
    sys.exit(main())
