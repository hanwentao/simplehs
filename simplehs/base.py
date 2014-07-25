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

    def __init__(self, agents, rng=None):
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
        self.who.draw(3)
        self.who.opponent.draw(4)
        self.state = Game.REPLACING
        self.winner = None

    def __str__(self):
        return '({turn_num}, {who}, {player0}, {player1})'.format(
            turn_num=self.turn_num,
            who=self.who.name,
            player0=self.players[0],
            player1=self.players[1],
        )

    def next_turn(self):
        if self.turn_num is not None:
            # XXX: To implement as a triggered event
            self.who.hero.reset()
            for minion in self.who.battlefield:
                minion.reset()
            self.trigger('turn_end', self.who)
            self.who._info('Turn #{turn_num} ended', turn_num=self.turn_num)
            self.who = self.who.opponent
            self.turn_num += 1
        else:
            self.state = Game.PLAYING
            self.turn_num = 0
            # TODO: Get a coin for the opponent
        if self.who.full_mana < 10:
            self.who.full_mana += 1
        self.who.mana = self.who.full_mana
        self.who._info('Turn #{turn_num} started', turn_num=self.turn_num)
        self.trigger('turn_start', self.who)
        self.who.draw()
        self.check()

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

    def trigger(self, event, *args, **kwargs):
        pass

    def check(self):
        for character in self.all_characters():
            if character.health <= 0:
                character.destroy()
        player0, player1 = self.players
        if player0.hero.health <= 0 and player1.hero.health <= 0:
            raise GameOver()  # Draw
        elif player0.hero.health <= 0:
            raise GameOver(player1)
        elif player1.hero.health <= 0:
            raise GameOver(player0)

    def all_characters(self):
        return self.players[0].all_characters() + self.players[1].all_characters()


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
            self.game.next_turn()

    def play(self, card, *args, **kwargs):
        if card not in self.hand:
            raise PlayException('{card} is not your card'.format(card=card))
        card.play(*args, **kwargs)

    def attack(self, source, target):
        if source is not self.hero and source not in self.battlefield:
            raise AttackException('{character} is not your character'.format(character=source))
        if target is not self.opponent.hero and target not in self.opponent.battlefield:
            raise AttackException('{character} is not your enemy character'.format(character=target))
        source.attack_(target)

    def end(self):
        self._check_state()
        self.game.next_turn()

    def concede(self):
        self._check_state(active=False)
        self.game.concede(self)

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

    def all_characters(self):
        return [self.hero] + self.battlefield

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
        self.cost = cost

    def __str__(self):
        return '({name}, {cost})'.format(
            name=self.name,
            cost=self.cost,
        )

    def can_play(self):
        return self.cost <= self.owner.mana

    def play(self):
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
        self.owner._check_state()
        self._check_can_play()
        super().play()
        minion = self.owner._create(Minion, self.name, self.attack, self.health, **self.abilities)
        minion.card = self
        if position is None:
            position = self.owner.battlefield.size
        self.owner.battlefield.insert(position, minion)
        self.owner._info('Summoned {minion} at {position}',
                          minion=minion, position=position)
        if 'battlecry' in minion.abilities:
            battlecry = minion.abilities.battlecry
            args = Dict()
            if getattr(battlecry, 'need_target', False):
                args.target = target
            battlecry(**args)

    def _check_can_play(self):
        super()._check_can_play()
        if self.owner.battlefield.size >= 7:
            raise PlayException('battlefield is full')


class SpellCard(Card):
    pass


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

    def __init__(self, name, attack, health):
        super().__init__(name)
        self.attack = attack
        self.health = health
        self.full_health = health
        self.attack_count = 0
        self.attack_limit = 1
        self.abilities = Dict()

    def __str__(self):
        return '({name}{abilities}, {attack}, {health}/{full_health})'.format(
            name=self.name,
            attack=self.attack,
            health=self.health,
            full_health=self.full_health,
            abilities='*' if self.abilities else '',
        )

    @property
    def charge(self):
        return self.abilities.get('charge', False)

    def reset(self):
        self.attack_count = 0

    def can_attack(self):
        return self.attack > 0 and self.attack_count < self.attack_limit

    def attack_(self, target):
        self.owner._check_state()
        self._check_can_attack()
        self.owner._info('{subject} was attacking {object}.', subject=self, object=target)
        target.deal_damage(self)
        self.deal_damage(target)
        self.attack_count += 1

    def _check_can_attack(self):
        if self.attack <= 0:
            raise AttackException('{character} has no attack'.format(character=self))
        if self.attack_count >= self.attack_limit:
            raise AttackException('{character} is exhausted'.format(character=self))

    def deal_damage(self, target):
        if self.attack > 0:
            target.take_damage(self.attack)

    def take_damage(self, damage):
        self.owner._info('{subject} took {damage} damage.', subject=self, damage=damage)
        self.health -= damage

    def destroy(self):
        self.owner._info('{subject} destroyed.', subject=self)


class Hero(Character):
    """An instance of hero."""

    def __init__(self, name, health):
        super().__init__(name, 0, health)
        self.armor = 0

    def __str__(self):
        return '({name}{abilities}, {attack}, {health}/{full_health}, {armor})'.format(
            name=self.name,
            attack=self.attack,
            health=self.health,
            full_health=self.full_health,
            armor=self.armor,
            abilities='*' if self.abilities else '',
        )


class Minion(Character):
    """An instance of minion."""

    def __init__(self, name, attack, health, **kwargs):
        super().__init__(name, attack, health)
        self.abilities = Dict(kwargs)
        self.sleeping = not self.charge

    def reset(self):
        super().reset()
        self.sleeping = False

    def can_attack(self):
        return super().can_attack() and not self.sleeping

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
