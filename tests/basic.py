#!/usr/bin/env python3

import unittest

from simplehs import *
from simplehs.heroes import *
from simplehs.cards import *


class TestGame(unittest.TestCase):

    def setUp(self):
        alice_agent = Dict(
            name='Alice',
            hero=Innkeeper,
            deck=[BloodfenRaptor] * 30,
        )
        bob_agent = Dict(
            name='Bob',
            hero=Innkeeper,
            deck=[RiverCrocolisk] * 30,
        )
        agents = (alice_agent, bob_agent)
        self.game = Game(agents)

    #def tearDown(self):
    #    print(self.game)

    def test_init(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        self.assertEqual(game.state, Game.REPLACING)
        self.assertIsNone(game.turn_num)
        self.assertTrue(alice.go_first)
        self.assertFalse(bob.go_first)
        self.assertEqual(alice.hand.size, 3)
        self.assertEqual(bob.hand.size, 4)
        self.assertEqual(alice.deck.size, 27)
        self.assertEqual(bob.deck.size, 26)
        self.assertEqual(alice.battlefield.size, 0)
        self.assertEqual(bob.battlefield.size, 0)

    def test_replace(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        # TODO: Really replace cards
        alice.replace()
        with self.assertRaises(StateException):
            alice.replace()
        bob.replace()
        self.assertEqual(game.state, Game.PLAYING)
        with self.assertRaises(StateException):
            bob.replace()

    def test_play(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        with self.assertRaises(StateException):
            alice.play(alice.hand[0])
        alice.replace()
        bob.replace()
        self.assertEqual(alice.hand.size, 4)
        with self.assertRaises(PlayException):
            alice.play(alice.hand[0])
        with self.assertRaises(StateException):
            bob.play(bob.hand[0])
        alice.end()
        bob.end()
        self.assertEqual(alice.hand.size, 5)
        alice.play(alice.hand[0])
        self.assertEqual(alice.hand.size, 4)
        self.assertEqual(alice.battlefield.size, 1)
        with self.assertRaises(PlayException):
            alice.play(bob.hand[0])

    def test_attack(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.replace()
        bob.replace()
        alice.end()
        bob.end()
        alice.play(alice.hand[0])
        minion = alice.battlefield[0]
        with self.assertRaises(AttackException):
            alice.attack(minion, bob.hero)
        alice.end()
        bob.end()
        self.assertEqual(bob.hero.health, 30)
        alice.attack(minion, bob.hero)
        self.assertEqual(bob.hero.health, 27)

    def test_end(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.replace()
        bob.replace()
        with self.assertRaises(StateException):
            bob.end()
        self.assertEqual(alice.mana, 1)
        alice.end()
        bob.end()
        self.assertEqual(alice.mana, 2)

    def test_concede(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.replace()
        bob.replace()
        with self.assertRaises(GameOver):
            bob.concede()

    def test_coin(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        alice.replace()
        bob.replace()
        self.assertEqual(bob.hand.size, 5)
        alice.end()
        with self.assertRaises(PlayException):
            bob.play(bob.hand[0])
        bob.play(bob.hand[-2])
        bob.play(bob.hand[0])
