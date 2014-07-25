#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestCharge(unittest.TestCase):

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

    def test_charge(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.acquire(BloodfenRaptor)
        alice.play(alice.hand[-1])
        raptor = alice.battlefield[-1]
        self.assertFalse(raptor.charge)
        with self.assertRaises(AttackException):
            alice.attack(raptor, bob.hero)
        alice.end()
        bob.end()
        self.assertEqual(bob.hero.health, 30)
        alice.attack(raptor, bob.hero)
        self.assertEqual(bob.hero.health, 27)
        alice.acquire(StonetuskBoar)
        alice.play(alice.hand[-1])
        boar = alice.battlefield[-1]
        self.assertTrue(boar.charge)
        alice.attack(boar, bob.hero)
        self.assertEqual(bob.hero.health, 26)
