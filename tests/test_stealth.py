#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestStealth(unittest.TestCase):

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

    def test_taunt(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.acquire(WorgenInfiltrator)
        alice.play(alice.hand[-1])
        infiltrator = alice.battlefield[-1]
        self.assertTrue(infiltrator.stealth)
        alice.end()
        bob.acquire(StonetuskBoar)
        bob.play(bob.hand[-1])
        boar = bob.battlefield[-1]
        with self.assertRaises(AttackException):
            bob.attack(boar, infiltrator)
        bob.end()
        alice.attack(infiltrator, bob.hero)
        self.assertFalse(infiltrator.stealth)
        alice.end()
        bob.attack(boar, infiltrator)
