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
        if not action.signature:
            action.signature = Dict()
        action.signature.update(kwargs)
        return action
    return wrapper

def add_target(target):
    return signature(target=target)


# Actions

def deal_damage(amount, target=None, split=False):
    @signature(target='target', is_spell='is_spell', spell_damage='spell_damage', game='game')
    def do_deal_damage(target, is_spell=False, spell_damage=0, game=None):
        if not isinstance(target, list):
            target = [target]
        else:
            target = target[:]
        damage = amount + int(is_spell) * spell_damage
        if not split:
            for character in target:
                character.take_damage(damage)
        else:
            for missile_num in range(damage):
                character = game.rng.choice(target)
                character.take_damage(1)
                if character.health <= 0:
                    target.remove(character)
    if target is None:
        do_deal_damage = needs_target()(do_deal_damage)
    else:
        do_deal_damage = add_target(target)(do_deal_damage)
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

def trigger(timing, filter, action):
    @signature(**action.signature)
    def do_trigger(real_timing, **kwargs):
        if real_timing != timing:
            return
        game = kwargs['filter_game']
        character = kwargs['filter_character']
        del kwargs['filter_game']
        del kwargs['filter_character']
        if not filter(game, character):
            return
        return action(**kwargs)
    return do_trigger


# Filters

def is_owner(game, character):
    return game.who is character.owner
