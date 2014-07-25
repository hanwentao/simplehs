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

    def test_init(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
        self.assertEqual(game.state, Game.REPLACING)
        self.assertIsNone(game.turn_num)
        self.assertTrue(alice.go_first)
        self.assertFalse(bob.go_first)
        self.assertEqual(len(alice.hand), 3)
        self.assertEqual(len(bob.hand), 4)
        self.assertEqual(len(alice.deck), 27)
        self.assertEqual(len(bob.deck), 26)
        self.assertEqual(len(alice.battlefield), 0)
        self.assertEqual(len(bob.battlefield), 0)

    def test_replace(self):
        game = self.game
        alice = game.players[0]
        bob = game.players[1]
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
        self.assertEqual(game.state, Game.PLAYING)
        with self.assertRaises(PlayException):
            alice.play(alice.hand[0])
        with self.assertRaises(StateException):
            bob.play(bob.hand[0])
        alice.end()
        bob.end()
        alice.play(alice.hand[0])
        self.assertEqual(len(alice.battlefield), 1)
