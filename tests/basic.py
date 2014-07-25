#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestGame(unittest.TestCase):

    def setUp(self):
        self.alice_agent = Dict(
            name='Alice',
            hero=Innkeeper,
            deck=[Wisp] * 30,
        )
        self.bob_agent = Dict(
            name='Bob',
            hero=Innkeeper,
            deck=[Wisp] * 30,
        )

    def test_run(self):
        agents = (self.alice_agent, self.bob_agent)
        game = Game(agents)
        alice = game.players[0]
        bob = game.players[1]
        self.assertTrue(alice.go_first)
        self.assertFalse(bob.go_first)
        self.assertEqual(len(alice.hand), 3)
        self.assertEqual(len(bob.hand), 4)
        self.assertEqual(len(alice.deck), 27)
        self.assertEqual(len(bob.deck), 26)
        self.assertEqual(len(alice.battlefield), 0)
        self.assertEqual(len(bob.battlefield), 0)
