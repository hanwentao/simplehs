#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestSpellDamage(unittest.TestCase):

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

    def test_spell_damage(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.acquire(KoboldGeomancer)
        alice.play(alice.hand[-1])
        alice.acquire(Fireball)
        alice.play(alice.hand[-1], target=bob.hero)
        self.assertEqual(bob.hero.health, 23)
