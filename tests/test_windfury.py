#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestWindfury(unittest.TestCase):

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

    def test_windfury(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.acquire(YoungDragonhawk)
        alice.play(alice.hand[-1])
        dragonhawk = alice.battlefield[-1]
        alice.acquire(Wisp)
        alice.play(alice.hand[-1])
        wisp = alice.battlefield[-1]
        self.assertTrue(dragonhawk.windfury)
        self.assertFalse(wisp.windfury)
        alice.end()
        bob.end()
        alice.attack(dragonhawk, bob.hero)
        alice.attack(dragonhawk, bob.hero)
        with self.assertRaises(AttackException):
            alice.attack(dragonhawk, bob.hero)
        alice.attack(wisp, bob.hero)
        with self.assertRaises(AttackException):
            alice.attack(wisp, bob.hero)
