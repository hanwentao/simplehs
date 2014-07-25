#!/usr/bin/env python3

def deal_damage(damage):
    def do_deal_damage(target):
        target.take_damage(damage)
    do_deal_damage.need_target = True
    return do_deal_damage
