#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestDeathrattle(unittest.TestCase):

    def setUp(self):
        alice_agent = Dict(
            name='Alice',
            hero=Innkeeper,
            deck=[LootHoarder],
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

    def test_deathrattle(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.acquire(LootHoarder)
        alice.play(alice.hand[-1], target=bob.hero)
        hoarder = alice.battlefield[-1]
        alice.end()
        bob.acquire(StonetuskBoar)
        bob.play(bob.hand[-1])
        boar = bob.battlefield[-1]
        bob.attack(boar, hoarder)
        self.assertEqual(alice.hand.size, 1)
