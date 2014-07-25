#!/usr/bin/env python3
# Hearthstone Agent

from ..base import Agent
from ..utils import Dict


class DummyAgent(Agent):
    """A dummy agent."""

    def decide(self):
        return super().decide()


class NaiveAgent(Agent):
    """A naive agent."""

    def decide(self):
        if self.player.game.turn_num is None:
            action = Dict(name='replace')
            return action
        for card in self.player.hand:
            if card.can_play():
                action = Dict(name='play', card=card, position=0)
                if 'battlecry' in card.abilities:
                    battlecry = card.abilities.battlecry
                    if getattr(battlecry, 'need_target', False):
                        action.target = self.player.opponent.hero
                return action
        for minion in self.player.battlefield:
            if minion.can_attack():
                if len(self.player.opponent.battlefield) > 0:
                    target = self.player.opponent.battlefield[0]
                else:
                    target = self.player.opponent.hero
                action = Dict(name='attack', subject=minion, object=target)
                return action
        action = Dict(name='end')
        return action
