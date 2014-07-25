#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestDivineShield(unittest.TestCase):

    def setUp(self):
        alice_agent = Dict(
            name='Alice',
            hero=Innkeeper,
            deck=[],
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

    def test_divine_shield(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.acquire(ArgentSquire)
        alice.play(alice.hand[-1])
        squire = alice.battlefield[-1]
        self.assertTrue(squire.divine_shield)
        alice.end()
        bob.acquire(BloodfenRaptor)
        bob.play(bob.hand[-1])
        raptor = bob.battlefield[-1]
        bob.end()
        alice.end()
        bob.attack(raptor, squire)
        self.assertEqual(alice.battlefield.size, 1)
        self.assertFalse(squire.divine_shield)
        bob.end()
        alice.attack(squire, raptor)
        self.assertEqual(alice.battlefield.size, 0)
