#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestFireball(unittest.TestCase):

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

    def test_fireball_against_enemy_hero(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.acquire(Fireball)
        alice.play(alice.hand[-1], target=bob.hero)
        self.assertEqual(bob.hero.health, 24)
        alice.acquire(KoboldGeomancer)
        alice.play(alice.hand[-1])
        alice.acquire(Fireball)
        alice.play(alice.hand[-1], target=bob.hero)
        self.assertEqual(bob.hero.health, 17)

    def test_fireball_against_own_hero(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.acquire(Fireball)
        alice.play(alice.hand[-1], target=alice.hero)
        self.assertEqual(alice.hero.health, 24)

    def test_fireball_against_minor(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.end()
        bob.acquire(BloodfenRaptor)
        bob.play(bob.hand[-1])
        raptor = bob.battlefield[-1]
        bob.end()
        alice.acquire(Fireball)
        alice.play(alice.hand[-1], target=raptor)
        self.assertEqual(bob.battlefield.size, 0)

    def test_fireball_against_major(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.end()
        bob.acquire(BoulderfistOgre)
        bob.play(bob.hand[-1])
        ogre = bob.battlefield[-1]
        bob.end()
        alice.acquire(Fireball)
        alice.play(alice.hand[-1], target=ogre)
        self.assertEqual(bob.battlefield.size, 1)
