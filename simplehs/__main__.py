#!/usr/bin/env python3
# Simple Hearthstone

import logging
import sys

from .base import Game
from .agents import *
from .heroes import *
from .cards import *


def main(args=sys.argv[1:]):
    logging.basicConfig(level=logging.DEBUG)
    agent0 = NaiveAgent('Alice')
    agent0.hero = Innkeeper
    agent0.deck = [ElvenArcher] * 30
    agent1 = NaiveAgent('Bob')
    agent1.hero = Innkeeper
    agent1.deck = [IronforgeRifleman] * 30
    agents = (agent0, agent1)
    game = Game(agents)
    game.run()


if __name__ == '__main__':
    sys.exit(main())
