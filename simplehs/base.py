#!/usr/bin/env python3
# Base classes

import logging

from .utils import Dict
from .utils import List
from .utils import Random
from .utils import get_class


class GameOver(Exception):
    """An exception that indicates the game is over."""

    def __init__(self, winner=None):
        super().__init__()
        self.winner = winner


class GameException(Exception):
    """An exception that indicates something wrong in the game."""
    pass

class StateException(GameException):
    """An exception that indicates an invalid state for some action."""
    pass

class PlayException(GameException):
    """An exception that indicates an invalid play action."""
    pass

class AttackException(GameException):
    """An exception that indicates an invalid attack action."""
    pass


class Game:
    """An instance of Hearthstone game."""

    REPLACING = '<replacing>'
    PLAYING = '<playing>'
    FINISHED = '<finished>'

    def __init__(self, agents, rng=None, debug=False):
        self.debug = debug
        self._date = 0
        # Set up random number generator
        self.rng = rng if rng is not None else Random()
        # Set up the two players
        agent0, agent1 = agents
        player0 = Player(self, agent0)
        player1 = Player(self, agent1)
        agent0.player = player0
        agent1.player = player1
        self.players = (player0, player1)
        player0.opponent = player1
        player1.opponent = player0
        # Decide who goes first
        self.turn_num = None
        self.who = self.rng.choice(self.players)
        self.who.go_first = True
        self.who.opponent.go_first = False
        # Draw the starting hands
        if not self.debug:
            self.who.draw(3)
            self.who.opponent.draw(4)
        self.winner = None
        if not self.debug:
            self.state = Game.REPLACING
        else:
            self.state = Game.PLAYING
            self.next_turn()

    def __str__(self):
        return '({turn_num}, {who}, {player0}, {player1})'.format(
            turn_num=self.turn_num,
            who=self.who.name,
            player0=self.players[0],
            player1=self.players[1],
        )

    @property
    def characters(self):
        return self.players[0].characters + self.players[1].characters

    def next_turn(self):
        if self.turn_num is not None:
            # XXX: To implement as a triggered event
            self.who.hero.reset()
            for minion in self.who.battlefield:
                minion.reset()
            self.who._info('Turn #{turn_num} ended', turn_num=self.turn_num)
            self.trigger('at turn_end')
            self.check_finish()
            self.who = self.who.opponent
            self.turn_num += 1
        else:
            self.turn_num = 0
            if not self.debug:
                from .cards.special import TheCoin
                self.who.opponent.acquire(TheCoin)
        if self.who.full_mana < 10:
            self.who.full_mana += 1
        self.who.mana = self.who.full_mana
        self.who._info('Turn #{turn_num} started', turn_num=self.turn_num)
        self.trigger('at turn_start')
        self.check_finish()
        if not self.debug:
            self.who.draw()
            self.check_finish()
        self.check()

    def check_finish(self):
        player0, player1 = self.players
        if player0.hero.health <= 0 and player1.hero.health <= 0:
            self.finish(None)  # It's a tie.
        elif player0.hero.health <= 0:
            self.finish(player1)
        elif player1.hero.health <= 0:
            self.finish(player0)

    def finish(self, winner):
        self.state = Game.FINISHED
        self.winner = winner
        raise GameOver(winner)

    def concede(self, who):
        self.finish(who.opponent)

    def run(self):
        # Replace the starting hands
        action = self.who.agent.decide()
        if action.name == 'replace':
            self.who.do_action(action)
        action = self.who.opponent.agent.decide()
        if action.name == 'replace':
            self.who.opponent.do_action(action)
        # Game begins
        try:
            for self.turn_num in range(98):
                if self.who.full_mana < 10:
                    self.who.full_mana += 1
                self.who.mana = self.who.full_mana
                self.who._info('Turn #{turn_num} started', turn_num=self.turn_num)
                self.trigger('turn_start', self.who)
                self.who.draw()
                self.check()
                while True:
                    # print(self)
                    action = self.who.agent.decide()
                    if action.name != 'replace':
                        end_turn = self.who.do_action(action)
                        if end_turn:
                            break
                # XXX: To implement as a triggered event
                self.who.hero.reset()
                for minion in self.who.battlefield:
                    minion.reset()
                self.trigger('turn_end', self.who)
                self.who._info('Turn #{turn_num} ended', turn_num=self.turn_num)
                self.who = self.who.opponent
            else:
                raise GameOver()
        except GameOver as result:
            print(self)
            if result.winner is not None:
                logging.info('{name} won.'.format(name=result.winner.name))
            else:
                logging.info('Game tied.')

    def _fetch_and_add_date(self):
        date = self._date
        self._date += 1
        return date

    def create(self, class_, *args, **kwargs):
        object = class_(*args, **kwargs)
        object.game = self
        object.dob = self._fetch_and_add_date()
        return object

    def trigger(self, timing):
        for character in self.characters:
            if character.trigger:
                args = character.owner._expand(character.trigger.signature)
                character.trigger(timing,
                                  filter_game=self,
                                  filter_character=character,
                                  **args)

    def check(self):
        for character in self.characters:
            if character.health <= 0:
                character.destroy()
        player0, player1 = self.players
        if player0.hero.health <= 0 and player1.hero.health <= 0:
            raise GameOver()  # Draw
        elif player0.hero.health <= 0:
            raise GameOver(player1)
        elif player1.hero.health <= 0:
            raise GameOver(player0)


class Agent:
    """An instance of an agent."""

    def __init__(self, name, hero=None, deck=None, player=None):
        self.name = name
        self.hero = hero
        self.deck = deck
        self.player = player

    def decide(self):
        action = Dict()
        action.name = 'end'
        return action


class Deck(List):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fatigue = 0

    def draw(self):
        if len(self) > 0:
            return self.pop(0)
        else:
            self.fatigue += 1
            return self.fatigue


class Hand(List):

    def acquire(self, card):
        if len(self) < 10:
            self.append(card)
        else:
            logging.info('{name}: Hand is full, {card} destroyed.'.format(
                name=self.owner.name,
                card=card,
            ))


class Battlefield(List):
    pass


class Player:
    """An instance of game player."""

    def __init__(self, game, agent):
        self.game = game
        self.agent = agent
        self.name = agent.name
        self.go_first = None
        self.replaced = False
        self.deck = Deck()
        self.deck.owner = self
        self.hand = Hand()
        self.hand.owner = self
        self.battlefield = Battlefield()
        self.battlefield.owner = self
        # TODO: secrets
        self.mana = 0
        self.full_mana = 0
        hero_class = get_class(agent.hero)
        self.hero = self._create(hero_class)
        for card in agent.deck:
            card_class = get_class(card)
            card = self._create(card_class)
            self.deck.append(card)
        self.game.rng.shuffle(self.deck)

    def __str__(self):
        return '({name}{go_first}, {mana}/{full_mana}, {hero}, {battlefield}, {hand}, {deck})'.format(
            name=self.name,
            go_first='+' if self.go_first else '',
            mana=self.mana,
            full_mana=self.full_mana,
            hero=self.hero,
            battlefield=self.battlefield,
            hand=self.hand,
            deck=self.deck.size,
        )

    @property
    def characters(self):
        return [self.hero] + self.minions

    @property
    def minions(self):
        return self.battlefield[:]

    @property
    def spell_damage(self):
        return sum(character.spell_damage for character in self.characters)

    def replace(self, cards=None):
        if self.game.state != Game.REPLACING:
            raise StateException('game is not replacing cards')
        if self.replaced:
            raise StateException('already replaced cards')
        if cards is None:
            cards = []
        blanks = []
        for card in cards:
            index = self.hand.index(card)
            blanks.append(index)
            new_index = self.game.rng.randrange(self.deck.size + 1)
            self.deck.insert(new_index, card)
        blanks.sort()
        for index in blanks:
            card = self.deck.pop(0)
            self.hand[index] = card
        self.replaced = True
        if self.opponent.replaced:
            self.game.state = Game.PLAYING
            self.game.next_turn()

    def play(self, card, *args, **kwargs):
        self._check_state()
        if card not in self.hand:
            raise PlayException('{card} is not your card'.format(card=card))
        card.play(*args, **kwargs)
        self.game.check_finish()

    def attack(self, source, target):
        self._check_state()
        if source is not self.hero and source not in self.battlefield:
            raise AttackException('{character} is not your character'.format(character=source))
        if target is not self.opponent.hero and target not in self.opponent.battlefield:
            raise AttackException('{character} is not your enemy character'.format(character=target))
        source.attack_(target)
        self.game.check_finish()

    def end(self):
        self._check_state()
        self.game.next_turn()

    def concede(self):
        if self.game.state == Game.FINISHED:
            raise StateException('game is already finished')
        self.game.concede(self)

    def draw(self, num_cards=1):
        for card_num in range(num_cards):
            card = self.deck.draw()
            if isinstance(card, Card):
                self.hand.acquire(card)
                self._info('Drew {card}.', card=card)
            else:
                fatigue = card
                self.hero.take_damage(fatigue)
                self._info('{hero} took {damage} fatigue damage.', hero=self.hero.name, damage=fatigue)

    def acquire(self, card_class):
        card = self._create(card_class)
        self.hand.append(card)

    def _check_state(self, active=True):
        if self.game.state != Game.PLAYING:
            raise StateException('game is not playing')
        if active and self.game.who is not self:
            raise StateException('not your turn')

    def _create(self, *args, **kwargs):
        object = self.game.create(*args, **kwargs)
        object.owner = self
        return object

    def _do_action(self, action):
        method = getattr(self, action.name)
        del action.name
        return method(**action)

    def _expand(self, signature, **kwargs):
        args = Dict()
        for name, symbol in signature.items():
            value = self._expand_symbol(symbol, **kwargs)
            args[name] = value
        return args

    def _expand_symbol(self, symbol, **kwargs):
        if symbol == 'self':
            return self
        elif symbol == 'enemy':
            return self.opponent
        elif symbol == 'target':
            return kwargs['target']
        elif symbol == 'spell_damage':
            return self.spell_damage
        elif symbol == 'is_spell':
            return kwargs.get('is_spell', False)
        else:
            raise ValueError('unknown symbol: {symbol}'.format(symbol=symbol))

    def _log(self, level, message, *args, **kwargs):
        message = self.name + ': ' + message.format(*args, **kwargs)
        logging.log(level, message)

    def _debug(self, message, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)

    def _info(self, message, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)

    def _warning(self, message, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)

    def _error(self, message, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)



class Ability:
    """A descriptor to hold ability with default value."""

    def __init__(self, name, default=None):
        self._name = '_' + name + '_'
        self._default = default

    def __get__(self, instance, owner):
        if hasattr(instance, self._name):
            value = getattr(instance, self._name)
        else:
            if type(self._default) is type:
                value = self._default()
            else:
                value = self._default
            setattr(instance, self._name, value)
        return value

    def __set__(self, instance, value):
        setattr(instance, self._name, value)

    def __delete__(self, instance):
        delattr(instance, self._name)


class Object:
    """An instance of game object."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Card(Object):
    """An instance of a card."""

    def __init__(self, name, cost):
        super().__init__(name)
        self._cost = cost

    def __str__(self):
        return '({name}, {cost})'.format(
            name=self.name,
            cost=self.cost,
        )

    @property
    def cost(self):
        if self.game.debug:
            return 0
        return self._cost

    def can_play(self):
        return self.cost <= self.owner.mana

    def play(self):
        self._check_can_play()
        self.owner.mana -= self.cost
        self.owner.hand.remove(self)

    def _check_can_play(self):
        if self.cost > self.owner.mana:
            raise PlayException('{mana} mana is not enough for {card}'.format(mana=self.owner.mana, card=self))


class MinionCard(Card):
    """An instance of a minion card."""

    def __init__(self, name, cost, attack, health, **kwargs):
        super().__init__(name, cost)
        self.attack = attack
        self.health = health
        self.abilities = Dict(kwargs)

    def can_play(self):
        return super().can_play() and self.owner.battlefield.size < 7

    def play(self, position=None, **kwargs):
        if 'battlecry' in self.abilities:
            battlecry = self.abilities.get('battlecry', None)
            abilities = self.abilities.copy()
            del abilities.battlecry
        else:
            battlecry = None
            abilities = self.abilities
        super().play()
        minion = self.owner._create(Minion, self.name, self.attack, self.health, **abilities)
        minion.card = self
        if position is None:
            position = self.owner.battlefield.size
        self.owner.battlefield.insert(position, minion)
        self.owner._info('Summoned {minion} at {position}',
                          minion=minion, position=position)
        if battlecry:
            args = self.owner._expand(battlecry.signature, **kwargs)
            battlecry(**args)

    def _check_can_play(self):
        super()._check_can_play()
        if self.owner.battlefield.size >= 7:
            raise PlayException('battlefield is full')


class SpellCard(Card):
    """An instance of a spell card."""

    def __init__(self, name, cost, effect, **kwargs):
        super().__init__(name, cost)
        self.effect = effect
        self.abilities = Dict(kwargs)

    def can_play(self):
        # TODO: Check target
        return super().can_play()

    def play(self, **kwargs):
        kwargs['is_spell'] = True
        args = self.owner._expand(self.effect.signature, **kwargs)
        super().play()
        self.effect(**args)

    def _check_can_play(self):
        super()._check_can_play()
        # TODO: Check target



class SecretCard(SpellCard):
    pass


class WeaponCard(Card):
    pass


class Entity(Object):
    """An instance of game entity (on the board)."""

    def __init__(self, name):
        super().__init__(name)


class Character(Entity):
    """An instance of character."""

    _sleeping = Ability('sleeping', False)
    _cant_attack = Ability('cant_attack', False)
    _charge = Ability('charge', False)
    _divine_shield = Ability('divine_shield', False)
    _stealth = Ability('stealth', False)
    _taunt = Ability('taunt', False)
    _windfury = Ability('windfury', False)
    _spell_damage = Ability('spell_damage', 0)
    _deathrattle = Ability('deathrattle', None)
    _trigger = Ability('trigger', None)

    def __init__(self, name, attack, health):
        super().__init__(name)
        self.attack = attack
        self.health = health
        self.full_health = health
        self.attack_count = 0

    def __str__(self):
        return '({name}{separator}{status}, {attack}, {health}/{full_health})'.format(
            name=self.name,
            attack=self.attack,
            health=self.health,
            full_health=self.full_health,
            separator=':' if self.status else '',
            status=self.status,
        )

    @property
    def status(self):
        result = ''
        if self.sleeping:
            result += 'z'
        if self.cant_attack:
            result += 'a'
        if self.charge:
            result += 'C'
        if self.divine_shield:
            result += 'D'
        if self.stealth:
            result += 'S'
        if self._taunt:  # For Stealth
            result += 'T'
        if self.windfury:
            result += 'W'
        if self.spell_damage:
            result += str(self.spell_damage)
        if self.deathrattle:
            result += '~'
        if self.trigger:
            result += '*'
        return result

    @property
    def sleeping(self):
        return not self.charge and self._sleeping

    @property
    def cant_attack(self):
        return self._cant_attack

    @property
    def charge(self):
        return self._charge

    @property
    def divine_shield(self):
        return self._divine_shield

    @property
    def stealth(self):
        return self._stealth

    @property
    def taunt(self):
        return not self.stealth and self._taunt

    @property
    def windfury(self):
        return self._windfury

    @property
    def spell_damage(self):
        return self._spell_damage

    @property
    def deathrattle(self):
        return self._deathrattle

    @property
    def trigger(self):
        return self._trigger

    @property
    def attack_limit(self):
        if self.cant_attack:
            return 0
        elif self.windfury:
            return 2
        else:
            return 1

    def reset(self):
        self._sleeping = False
        self.attack_count = 0

    def can_attack(self):
        return self.attack > 0 and self.attack_count < self.attack_limit

    def attack_(self, target):
        self._check_can_attack(target)
        self.owner._info('{subject} was attacking {object}.', subject=self, object=target)
        self.attack_count += 1
        self._stealth = False
        target.deal_damage(self)
        self.deal_damage(target)

    def _check_can_attack(self, target):
        if self.attack <= 0:
            raise AttackException('{character} has no attack'.format(character=self))
        if self.attack_count >= self.attack_limit:
            raise AttackException('{character} is exhausted'.format(character=self))
        if target.stealth:
            raise AttackException('{target} is stealth'.format(target=target))
        if any(character.taunt for character in target.owner.characters) and not target.taunt:
            raise AttackException('{target} is not taunt, but taunt exists'.format(target=target))

    def deal_damage(self, target):
        if self.attack > 0:
            target.take_damage(self.attack)

    def take_damage(self, damage):
        self.owner._info('{subject} took {damage} damage.', subject=self, damage=damage)
        if self.divine_shield:
            self._divine_shield = False
        else:
            self.health -= damage
        if self.health <= 0:
            self.destroy()

    def destroy(self):
        self.owner._info('{subject} destroyed.', subject=self)
        deathrattle = self.deathrattle
        if deathrattle:
            args = self.owner._expand(deathrattle.signature)
            deathrattle(**args)


class Hero(Character):
    """An instance of hero."""

    def __init__(self, name, health):
        super().__init__(name, 0, health)
        self.armor = 0

    def __str__(self):
        return '({name}{status}, {attack}, {health}/{full_health}, {armor})'.format(
            name=self.name,
            attack=self.attack,
            health=self.health,
            full_health=self.full_health,
            armor=self.armor,
            status=self.status,
        )


class Minion(Character):
    """An instance of minion."""

    def __init__(self, name, attack, health, **kwargs):
        super().__init__(name, attack, health)
        self._sleeping = True
        for name, value in kwargs.items():
            setattr(self, '_' + name, value)

    def reset(self):
        super().reset()
        self._sleeping = False

    def can_attack(self):
        return super().can_attack() and not self.sleeping

    def _check_can_attack(self, target):
        super()._check_can_attack(target)
        if self.sleeping:
            raise AttackException('{minion} is sleeping'.format(minion=self))

    def destroy(self):
        self.owner.battlefield.remove(self)
        super().destroy()


class Weapon(Entity):
    pass


class Secret(Entity):
    pass


class Spell(Object):
    pass


class HeroPower(Spell):
    pass
