#!/usr/bin/env python3

def deal_damage(amount):
    def do_deal_damage(target):
        target.take_damage(amount)
    do_deal_damage.need_target = True
    return do_deal_damage

def gain_mana(amount, permanent=False, empty=False):
    def do_gain_mana(player):
        if not permanent:
            player.mana += amount
        else:
            player.full_mana = min(player.full_mana + amount, 10)
            if not empty:
                player.mana = min(player.mana + amount, player.full_mana)
    return do_gain_mana
