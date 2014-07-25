#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestTrigger(unittest.TestCase):

    def setUp(self):
        alice_agent = Dict(
            name='Alice',
            hero=Innkeeper,
            deck=[ManaTideTotem],
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

    def test_trigger(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.acquire(ManaTideTotem)
        alice.play(alice.hand[-1], target=bob.hero)
        totem = alice.battlefield[-1]
        self.assertEqual(alice.hand.size, 0)
        alice.end()
        self.assertEqual(alice.hand.size, 1)
        bob.end()
        self.assertEqual(alice.hand.size, 1)
        totem.destroy()
        alice.end()
        self.assertEqual(alice.hand.size, 1)
