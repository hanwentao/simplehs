#!/usr/bin/env python
# Simple Hearthstone

import argparse
import logging
import random
import sys
from collections import defaultdict

from base import Deck
from base import Match
from cards import *
from clients import *
from heroes import *


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='Simulate a Hearthstone match.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='be verbose (debug information)')
    parser.add_argument('-d', '--display', action='store_true',
                        help='display the board every time')
    parser.add_argument('-n', '--matches', type=int, default=1,
                        help='number of matches to play')
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
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    num_matches = args.matches
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
    result = defaultdict(int)
    random.seed(seed)
    max_num_turns = 0
    for match_num in xrange(num_matches):
        match_seed = random.random()
        match = Match(client1, client2, match_seed, display=args.display)
        winner, first, num_turns = match.run()
        result[winner] += 1
        result[first] += 1
        max_num_turns = max(max_num_turns, num_turns)
    print result, max_num_turns


if __name__ == '__main__':
    sys.exit(main())
