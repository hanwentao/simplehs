#!/usr/bin/env python3

from .utils import Dict


class ClosureWrapper:
    """A closure wrapper for default attribute."""

    def __init__(self, closure):
        self._closure = closure

    def __call__(self, *args, **kwargs):
        return self._closure(*args, **kwargs)

    def __getattr__(self, name):
        return None


# Decorators

def needs_target(filter=None):
    def wrapper(action):
        if not isinstance(action, ClosureWrapper):
            action = ClosureWrapper(action)
        action.needs_target = True
        action.targetable_filter = filter
        return action
    return wrapper

def signature(**kwargs):
    def wrapper(action):
        if not isinstance(action, ClosureWrapper):
            action = ClosureWrapper(action)
        action.signature = Dict(kwargs)
        return action
    return wrapper


# Actions

def deal_damage(amount):
    @needs_target()
    @signature(target='target', is_spell='is_spell', spell_damage='spell_damage')
    def do_deal_damage(target, is_spell=False, spell_damage=0):
        target.take_damage(amount + int(is_spell) * spell_damage)
    return do_deal_damage

def draw_card(num_cards, who='self'):
    @signature(player=who)
    def do_draw_card(player):
        player.draw(num_cards)
    return do_draw_card

def gain_mana(amount, permanent=False, empty=False, who='self'):
    @signature(player=who)
    def do_gain_mana(player):
        if not permanent:
            player.mana += amount
        else:
            player.full_mana = min(player.full_mana + amount, 10)
            if not empty:
                player.mana = min(player.mana + amount, player.full_mana)
    return do_gain_mana
