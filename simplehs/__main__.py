#!/usr/bin/env python
# Simple Hearthstone

import argparse
import logging
import sys

from base import Deck
from base import Match
from cards import *
from clients import *
from heroes import *

logging.basicConfig(level=logging.DEBUG)


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Simulate a Hearthstone match.')
    parser.add_argument('-s', '--seed', type=int, default=1,
                        help='random seed')
    parser.add_argument('--client1', default='DummyClient',
                        help='client class of player 1')
    parser.add_argument('--client2', default='DummyClient',
                        help='client class of player 2')
    parser.add_argument('--name1', default='Alice',
                        help='name of player 1')
    parser.add_argument('--name2', default='Bob',
                        help='name of player 2')
    parser.add_argument('--hero1', default='InnKeeper',
                        help='hero class of player 1')
    parser.add_argument('--hero2', default='InnKeeper',
                        help='hero class of player 2')
    args = parser.parse_args()
    seed = args.seed
    client1_class = globals()[args.client1]
    client2_class = globals()[args.client2]
    name1 = args.name1
    name2 = args.name2
    hero1_class = globals()[args.hero1]
    hero2_class = globals()[args.hero2]
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
    client1 = client1_class(name1, hero1_class, deck)
    client2 = client2_class(name2, hero2_class, deck)
    match = Match(client1, client2, seed)
    match.run()


if __name__ == '__main__':
    sys.exit(main())
