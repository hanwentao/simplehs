#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestCantAttack(unittest.TestCase):

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
        alice.acquire(AncientWatcher)
        alice.play(alice.hand[-1])
        watcher = alice.battlefield[-1]
        self.assertTrue(watcher.cant_attack)
        alice.end()
        bob.acquire(BloodfenRaptor)
        bob.play(bob.hand[-1])
        raptor = bob.battlefield[-1]
        bob.end()
        with self.assertRaises(AttackException):
            alice.attack(watcher, bob.hero)
        alice.end()
        bob.attack(raptor, watcher)
        self.assertEqual(bob.battlefield.size, 0)
        self.assertEqual(alice.battlefield.size, 1)
