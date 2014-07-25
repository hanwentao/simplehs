#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestDrawCard(unittest.TestCase):

    def setUp(self):
        alice_agent = Dict(
            name='Alice',
            hero=Innkeeper,
            deck=[NoviceEngineer],
        )
        bob_agent = Dict(
            name='Bob',
            hero=Innkeeper,
            deck=[],
        )
        agents = (alice_agent, bob_agent)
        self.game = Game(agents, debug=True)

    #def tearDown(self):
    #    print(self.game)

    def test_draw_card(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.acquire(NoviceEngineer)
        alice.play(alice.hand[-1], target=bob.hero)
        self.assertEqual(alice.hand.size, 1)
