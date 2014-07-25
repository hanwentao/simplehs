#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.utils import MockRandom
from simplehs.heroes import *
from simplehs.cards import *


class TestArcaneMissiles(unittest.TestCase):

    def setUp(self):
        alice_agent = Dict(
            name='Alice',
            hero=Mage,
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

    def test_arcane_missiles_against_enemy_hero(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.acquire(ArcaneMissiles)
        alice.play(alice.hand[-1])
        self.assertEqual(bob.hero.health, 27)
        alice.acquire(KoboldGeomancer)
        alice.play(alice.hand[-1])
        alice.acquire(ArcaneMissiles)
        alice.play(alice.hand[-1])
        self.assertEqual(bob.hero.health, 23)

    def test_arcane_missiles_against_minor(self):
        game = self.game
        game.rng = MockRandom([1, 1, 1])
        alice = game.players[0]
        bob = game.players[1]
        alice.end()
        bob.acquire(BloodfenRaptor)
        bob.play(bob.hand[-1])
        raptor = bob.battlefield[-1]
        self.assertEqual(bob.battlefield.size, 1)
        bob.end()
        alice.acquire(ArcaneMissiles)
        alice.play(alice.hand[-1])
        self.assertEqual(bob.battlefield.size, 0)
        self.assertEqual(bob.hero.health, 29)

    def test_arcane_missiles_against_major(self):
        game = self.game
        game.rng = MockRandom([1, 1, 1])
        alice = game.players[0]
        bob = game.players[1]
        alice.end()
        bob.acquire(BoulderfistOgre)
        bob.play(bob.hand[-1])
        ogre = bob.battlefield[-1]
        self.assertEqual(bob.battlefield.size, 1)
        bob.end()
        alice.acquire(ArcaneMissiles)
        alice.play(alice.hand[-1])
        self.assertEqual(bob.battlefield.size, 1)
        self.assertEqual(ogre.health, 4)
        self.assertEqual(bob.hero.health, 30)
