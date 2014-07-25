#!/usr/bin/env python3

import collections
import io
import json
import re
import sys

from utils import Dict
from utils import pascalize


RARITY_CODE = {
    0: 'free',
    1: 'common',
    3: 'rare',
    4: 'epic',
    5: 'legendary',
}

CLASS_CODE = collections.OrderedDict()
CLASS_CODE[11] = 'druid'
CLASS_CODE[3] = 'hunter'
CLASS_CODE[8] = 'mage'
CLASS_CODE[2] = 'paladin'
CLASS_CODE[5] = 'priest'
CLASS_CODE[4] = 'rogue'
CLASS_CODE[7] = 'shaman'
CLASS_CODE[9] = 'warlock'
CLASS_CODE[1] = 'warrior'
CLASS_CODE[0] = 'neutral'

TYPE_CODE = {
    4: 'minion',
    5: 'spell',
    7: 'weapon',
}

RACE_CODE = {
    0: 'neutral',
    14: 'murloc',
    15: 'demon',
    20: 'beast',
    21: 'totem',
    23: 'pirate',
    24: 'dragon',
}


def convert(card_info):
    card = Dict()
    card.name = card_info['name']
    card.type = TYPE_CODE[card_info['type']]
    card.cost = int(card_info['cost'])
    card.rarity = RARITY_CODE[card_info['quality']]
    card.class_ = CLASS_CODE[card_info.get('classs', 0)]
    card.description = card_info.get('description', '')
    if card.type == 'minion':
        card.attack = int(card_info['attack'])
        card.health = int(card_info['health'])
    elif card.type == 'weapon':
        card.attack = int(card_info['attack'])
        card.durability = int(card_info['durability'])
    return card


ABILITIES = ['taunt', 'charge', 'windfury', 'stealth', 'divine shield']

def segment(text):
    if not text:
        return []
    text = text.lower()
    pieces = text.split(', ')
    if any(p in ABILITIES for p in pieces):
        return pieces
    pieces = text.split('  ')
    pieces = [p.rstrip('.') for p in pieces]
    return pieces


MATCHERS = []

def matcher(func):
    """A decorator which indicates a description matcher."""
    MATCHERS.append(func)
    return func

@matcher
def taunt(text):
    if text == 'taunt':
        return ('taunt', True)

@matcher
def charge(text):
    if text == 'charge':
        return ('charge', True)

#@matcher
def windfury(text):
    if text == 'windfury':
        return ('windfury', True)

#@matcher
def divine_shield(text):
    if text == 'divine shield':
        return ('divine_shield', True)

#@matcher
def stealth(text):
    if text == 'stealth':
        return ('stealth', True)

#@matcher
def cant_attack(text):
    if text == "can't attack":
        return ('cant_attack', True)

#@matcher
def spell_damage(text):
    match = re.match(r'^spell damage \+(?P<spell_damage>\d+)$', text)
    if match:
        spell_damage = int(match.group('spell_damage'))
        return ('spell_damage', spell_damage)

#@matcher
def overload(text):
    match = re.match(r'^overload: \((?P<overload>\d+)\)$', text)
    if match:
        return ('overload', match.group('overload'))

@matcher
def battlecry(text):
    if text.startswith('battlecry: '):
        result = process(text[len('battlecry: '):])
        if result is not None:
            return ('battlecry', result[1])

#@matcher
def deathrattle(text):
    if text.startswith('deathrattle: '):
        result = process(text[len('deathrattle: '):])
        if result is not None:
            return ('deathrattle', result)

#@matcher
def enrage(text):
    if text.startswith('enrage: '):
        match = re.match(r'^enrage: \+(?P<amount>\d+) attack$', text)
        if match:
            amount = match.group('amount')
            return ('enrage', 'add_enrage_attck({amount})'.format(**locals()))

#@matcher
def secret(text):
    if text.startswith('secret: '):
        pass  # TODO

#@matcher
def combo(text):
    if text.startswith('combo: '):
        pass  # TODO

#@matcher
def choose_one(text):
    if text.startswith('choose one - '):
        pass  # TODO

#@matcher
def trigger(text):
    match = re.match(r'^(?P<timing>at|when(ever)?|after) (?P<condition>.*?), (?P<action>.*)$', text)
    if match:
        timing = match.group('timing')
        timing = 'when' if timing == 'whenever' else timing  # XXX: when == before?
        condition = match.group('condition')
        action = match.group('action')
        action = process(action)
        if action is not None:
            return ('trigger', (timing, condition, action))

#@matcher
def if_(text):
    match = re.match(r'^if (?P<condition>.*?), (?P<action>.*)$', text)
    if match:
        condition = match.group('condition')
        action = match.group('action')
        action = process(action)
        if action is not None:
            pass  # TODO

#@matcher
def draw_card(text):
    match = re.match(r'^draw (a(?P<dream> dream)? card|(?P<quantity>\d+) cards)$', text)
    if match:
        if match.group('dream'):
            return ('action', 'draw_dream_card()')
        if match.group(1) == 'a card':
            num_cards = 1
        else:
            num_cards = match.group('quantity')
        return ('action', 'draw_card({num_cards})'.format(**locals()))

#@matcher
def discard_card(text):
    match = re.match(r'discard (?P<quantity>a|two) random cards?', text)
    if match:
        num_cards = 1 if match.group('quantity') == 'a' else 2
        return ('action', 'discard_card({num_cards})'.format(**locals()))

#@matcher
def put(text):
    match = re.match(r'^put (?P<what>.*?)( (from|in) (?P<source>.*?))?( into (?P<target>.*?))$', text)
    if match:
        what = match.group('what')
        source = match.group('source')
        target = match.group('target')
        return ('action', 'put("{what}", from_="{source}", to="{target}")'.format(**locals()))

@matcher
def deal_damage(text):
    match = re.match(r'^deal (?P<damage>\d+) damage( (to|randomly (?P<split>split) (between|among)) (?P<target>.*))?$', text)
    if match:
        damage = match.group('damage')
        target = match.group('target')
        split = match.group('split')
        if target is None:
            return ('action', 'deal_damage({damage})'.format(**locals()))
        return  # XXX
        parts = text.split(' and ')
        if len(parts) == 1:
            if not split:
                return ('action', 'deal_damage({damage}, target="{target}")'.format(**locals()))
            else:
                return ('action', 'deal_damage({damage}, split=True, target="{target}")'.format(**locals()))
        match = re.match(r'^deal (?P<damage>\d+) damage to (?P<target>.*)$', parts[0])
        damage = match.group('damage')
        target = match.group('target')
        match2 = re.match(r'^(?P<damage>\d+) damage to (?P<target>.*)$', parts[1])
        if match2:
            damage2 = match2.group('damage')
            target2 = match2.group('target')
            return ('action', ['deal_damage({damage}, target="{target}")'.format(**locals()),
                               'deal_damage({damage2}, target="{target2}")'.format(**locals())])
        action = process(parts[1])
        if action:
            return ('action', ['deal_damage({damage}, target="{target}")'.format(**locals()), action[1]])

#@matcher
def restore(text):
    match = re.match(r'^restore (?P<health>\d+) health( to (?P<target>.*))?$', text)
    if match:
        health = match.group('health')
        target = match.group('target')
        if target is None:
            return ('action', 'restore({health})'.format(**locals()))
        parts = target.split(' and ')
        if len(parts) == 1:
            return ('action', 'restore({health}, target=\'{target}\')'.format(**locals()))

#@matcher
def give(text):
    if text.startswith('give '):
        pass  # TODO

#@matcher
def gain(text):
    if text.startswith('gain '):
        pass  # TODO

#@matcher
def change(text):
    match = re.match(r'^(change|set) (?P<what>.*?) to (?P<value>.*)$', text)
    if match:
        what = match.group('what')
        value = match.group('value')
        pass  # TODO

#@matcher
def summon(text):
    match = re.match(r'^summon (?P<quantity>an?|two|three) (?P<what>.*?)( with (?P<ability>.*?))?( that (?P<trigger>.*?))?( for your (?P<opponent>opponent))?$', text)
    if match:
        quantity = match.group('quantity')
        quantity = parse_number(quantity)
        what = match.group('what')
        ability = match.group('ability')
        trigger = match.group('trigger')
        opponent = bool(match.group('opponent'))
        template = 'summon({quantity}, "{what}"'
        if ability: template += ', ability="{ability}"'
        if trigger: template += ', trigger="{trigger}"'
        if opponent: template += ', opponent={opponent}'
        template += ')'
        return ('action', template.format(**locals()))

#@matcher
def equip(text):
    match = re.match(r'^equip a (?P<what>.*)$', text)
    if match:
        what = match.group('what')
        return ('action', 'equip("{what}")'.format(**locals()))

#@matcher
def destroy(text):
    if text.startswith('destroy '):
        pass  # TODO

#@matcher
def return_(text):
    match = re.match(r'^return (?P<target>.*?)( from (.*?))? to (.*)$', text)
    if match:
        target = match.group('target')
        return ('action', 'return_(target="{target}")'.format(**locals()))

#@matcher
def freeze(text):
    match = re.match(r'^freeze (?P<target>.*)$', text)
    if match:
        target = match.group('target')
        return ('action', 'freeze("{target}")'.format(**locals()))

#@matcher
def silence(text):
    match = re.match(r'^silence (?P<target>.*)$', text)
    if match:
        parts = text.split(', then ')
        if len(parts) == 1:
            target = match.group('target')
            return ('action', 'silence("{target}")'.format(**locals()))
        match = re.match(r'^silence (?P<target>.*)$', parts[0])
        target = match.group('target')
        action = process(parts[1])
        return ('action', ['silence("{target}")'.format(**locals()), action[1]])

#@matcher
def take_control(text):
    match = re.match(r'^take control of (?P<target>.*)$', text)
    if match:
        target = match.group('target')
        return ('action', 'take_control("{target}")'.format(**locals()))

#@matcher
def transform(text):
    match = re.match(r'transform (?P<source>.*) into (?P<target>.*)', text)
    if match:
        source = match.group('source')
        target = match.group('target')
        return ('action', 'transform("{source}", "{target}")'.format(**locals()))


def process(piece):
    """Convert a piece of description text to source code."""

    for matcher in MATCHERS:
        result = matcher(piece)
        if result is not None:
            return result

def to_string(value):
    if type(value) is list:
        return '[' + ', '.join(item for item in value) + ']'
    else:
        return repr(value)


def generate_code(card):
    code = io.StringIO()
    card.class_name = pascalize(card.name)
    try:
        attributes = ()
        abilities = {}
        if card.type == 'minion':
            attributes = (card.attack, card.health)
        elif card.type == 'spell':
            pass
        elif card.type == 'weapon':
            attributes = (card.attack, card.durability)
        else:
            raise NotImplementedError()
        pieces = segment(card.description)
        remaining = pieces[:]
        for piece in pieces:
            result = process(piece)
            if result:
                key, value = result
                if key not in abilities:
                    abilities[key] = value
                elif type(abilities[key]) is not list:
                    abilities[key] = [abilities[key], value]
                else:
                    abilities[key].append(value)
                remaining.remove(piece)
        if remaining:
            raise NotImplementedError(repr(remaining))
        if card.type == 'spell':
            attributes = (abilities['action'],)
            del abilities['action']
        code.write('{class_name} = make_{type}_card("{name}", {cost}'.format(**card))
        if attributes:
            card.attributes = ', '.join(to_string(a) for a in attributes)
            code.write(', {attributes}'.format(**card))
        if abilities:
            card.abilities = ', '.join(k + '=' + to_string(v) for k, v in abilities.items())
            code.write(', {abilities}'.format(**card))
        code.write(')\n')
    except NotImplementedError as e:
        card.Type = card.type.capitalize()
        card.remaining = e.args
        code.write('# {Type} card {class_name} ({name}: {description}) unimplemented: {remaining}\n'.format(**card))
        success = False
    else:
        success = True
    return (code.getvalue(), success)


def main(args=sys.argv[1:]):
    with open('data/cards.json') as card_file:
        card_info_list = json.load(card_file)
    generated = 0
    class_ = None
    code_file = None
    class_total = collections.defaultdict(int)
    class_generated = collections.defaultdict(int)
    for card_info in sorted(card_info_list, key=lambda info: (info.get('classs', 0), info['cost'], info['name'])):
        card = convert(card_info)
        code, success = generate_code(card)
        class_total[card.class_] += 1
        if success:
            generated += 1
            class_generated[card.class_] += 1
        if card.class_ != class_:
            class_ = card.class_
            # XXX: Register names of card classes into __all__.
            code_file = open('cards/{class_}.py'.format(**locals()), 'w')
            code_file.write("""\
#!/usr/bin/env python3

from .utils import *

""")
        code_file.write(code)
    percentage = lambda n, d: '{}/{} {:0.2f}%'.format(n, d, 100.0 * n / d)
    with open('cards/__init__.py', 'w') as code_file:
        code_file.write("""\
#!/usr/bin/env python3

""")
        for class_ in CLASS_CODE.values():
            code_file.write('from .{class_} import *\n'.format(**locals()))
            print('{}: {}'.format(class_, percentage(class_generated[class_], class_total[class_])))
        code_file.write('from .special import *\n')
    print('total: {}'.format(percentage(generated, len(card_info_list))))


if __name__ == '__main__':
    sys.exit(main())
