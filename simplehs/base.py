# Base classes

import copy
import logging
import random


class Object(object):
    """An object"""

    def __init__(self, name):
        self._name = name
        self._owner = None

    @property
    def name(self):
        return self._name

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value


class Character(Object):
    """A character"""

    def __init__(self, name, attack, health):
        super(Character, self).__init__(name)
        self._base_attack = attack
        self._base_health = health
        self._sleeping = False
        self._num_attacks_allowed = 1
        self._num_attacks_done = 0

    def __str__(self):
        return str((self.name, self.attack, self.health))

    def __repr__(self):
        return str(self)

    @property
    def attack(self):
        return self._base_attack

    @property
    def health(self):
        return self._base_health

    def can_attack(self):
        return (self.attack > 0 and not self._sleeping and
                self._num_attacks_done < self._num_attacks_allowed)

    def reset_attack_status(self):
        self._sleeping = False
        self._num_attacks_done = 0

    def attack_(self, target):
        if not self.can_attack():
            logging.warning('Character [%s] cannot attack', self.name)
            return
        logging.info('Character [%s] attacked character [%s]',
                     self.name, target.name)
        self._num_attacks_done += 1
        target.take_damage(self.attack)
        self.take_damage(target.attack)

    def take_damage(self, damage):
        if damage <= 0:
            return
        logging.info('Character [%s] took %d damage', self.name, damage)
        self._base_health -= damage
        if self._base_health <= 0:
            self.die()

    def die(self):
        logging.info('Character [%s] died', self.name)


class Hero(Character):
    """A hero"""

    def __init__(self, name, health):
        super(Hero, self).__init__(name, 0, health)

    def die(self):
        super(Hero, self).die()
        raise MatchResult(self.owner.opponent, self.owner)


class Minion(Character):
    """A minion"""

    def __init__(self, name, attack, health):
        super(Minion, self).__init__(name, attack, health)
        self._sleeping = True

    def die(self):
        super(Minion, self).die()
        self._owner.battlefield.remove(self)


class Weapon(Object):
    pass


class Card(Object):
    """A card"""

    def __init__(self, name, cost):
        super(Card, self).__init__(name)
        self._cost = cost

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    @property
    def cost(self):
        return self._cost

    def can_play(self):
        enough_mana = self.cost <= self.owner.mana
        if not enough_mana:
            logging.debug('Not enough mana for card (%s): %d > %d',
                          self.name, self.cost, self.owner.mana)
        return enough_mana

    def play(self):
        logging.info('Player <%s> played a card (%s)',
                     self.owner.name, self.name)


class MinionCard(Card):
    """A minion card"""

    def __init__(self, name, cost, attack, health):
        super(MinionCard, self).__init__(name, cost)
        self._attack = attack
        self._health = health

    def can_play(self):
        enough_mana = Card.can_play(self)
        has_room = len(self.owner.battlefield) < 7
        if not has_room:
            logging.debug('No room for minion')
        return enough_mana and has_room

    @property
    def attack(self):
        return self._attack

    @property
    def health(self):
        return self._health

    def summon(self):
        return Minion(self.name, self.attack, self.health)

    def play(self):
        super(MinionCard, self).play()
        minion = self.summon()
        self.owner._mana -= self.cost
        self.owner.battlefield.append(minion)
        minion.owner = self.owner
        logging.info('Player <%s> summoned a minion [%s]',
                     self.owner.name, minion.name)


class SpellCard(Card):
    """A spell card"""

    def __init__(self, name, cost):
        super(SpellCard, self).__init__(name, cost)


class WeaponCard(Card):
    pass


class Player(object):
    """A player"""

    def __init__(self, match, client):
        self._match = match
        self._client = client
        self._opponent = None
        self._name = client.name
        self._first = None
        self._hero = client.hero_class()
        self._hero.owner = self
        self._deck = Deck(copy.deepcopy(client.deck))
        for card in self.deck:
            card.owner = self
        self._hand = Hand()
        self._battlefield = Battlefield()
        self._full_mana = 0
        self._mana = 0

    def __str__(self):
        return str((self.name,
                    self.hero,
                    self.mana,
                    self.full_mana,
                    self.battlefield,
                    self.hand,
                    self.deck,
                   ))

    @property
    def match(self):
        return self._match

    @property
    def client(self):
        return self._client

    @property
    def opponent(self):
        return self._opponent

    @opponent.setter
    def opponent(self, value):
        self._opponent = value

    @property
    def name(self):
        return self._name

    @property
    def first(self):
        return self._first

    @first.setter
    def first(self, value):
        self._first = value

    @property
    def hero(self):
        return self._hero

    @property
    def deck(self):
        return self._deck

    @property
    def hand(self):
        return self._hand

    @property
    def battlefield(self):
        return self._battlefield

    @property
    def full_mana(self):
        return self._full_mana

    @property
    def mana(self):
        return self._mana

    def regenerate(self):
        """Regenerate mana crystals."""
        self._full_mana = min(self._full_mana + 1, 10)
        self._mana = self._full_mana
        logging.info('Player <%s> regenerated %d mana', self.name, self.mana)

    def draw(self, num_cards=1):
        """Draw some cards."""
        for card_num in xrange(num_cards):
            success, card_or_fatigue = self.deck.draw()
            if success:
                card = card_or_fatigue
                self.hand.append(card)
                logging.info('Player <%s> drew a card (%s)',
                             self.name, card.name)
            else:
                fatigue = card_or_fatigue
                logging.info('Player <%s> took a fatigue of %d',
                             self.name, fatigue)
                self.hero.take_damage(fatigue)

    def replace(self):
        """Replace the starting hand."""
        card_index_list = self.client.replace(self)[1]
        cards = self.hand.remove_(card_index_list)
        self.draw(len(card_index_list))
        self.deck.put_back(cards, self.match.random)

    def play(self, card):
        """Play a card."""
        self.hand.remove(card)
        card.play()


class Deck(list):
    """A deck of cards"""

    def __init__(self, *args, **kwargs):
        super(Deck, self).__init__(*args, **kwargs)
        self._fatigue = 0

    def shuffle(self, random):
        random.shuffle(self)

    def draw(self):
        if len(self) > 0:
            return (True, self.pop(0))
        else:
            self._fatigue += 1
            return (False, self._fatigue)

    def put_back(self, cards, random):
        for card in cards:
            index = random.randint(0, len(self))
            self.insert(index, card)


class Hand(list):
    """A hand of cards"""

    def remove_(self, index_list):
        removed_cards = [self[index] for index in index_list]
        for card in removed_cards:
            self.remove(card)
        return removed_cards


class Battlefield(list):
    pass


class Client(object):
    """A Hearthstone client represents a player."""

    def __init__(self, name, hero_class, deck):
        self._name = name
        self._hero_class = hero_class
        self._deck = deck

    def __str__(self):
        return self._name

    def __repr__(self):
        return str(self)

    @property
    def name(self):
        return self._name

    @property
    def hero_class(self):
        return self._hero_class

    @property
    def deck(self):
        return self._deck

    def replace(self, me):
        return ('replace', [])

    def decide(self, me, enemy):
        return ('end', )


class Configuration(object):
    """Match configuration"""

    def __init__(self, *args, **kwargs):
        self._config = {}

    @property
    def coin(self):
        return self._config.get('coin', True)

    @coin.setter
    def coin(self, value):
        self._config['coin'] = value


class MatchResult(Exception):
    """Exception indicates the result of a match"""

    def __init__(self, winner, loser):
        self._winner = winner
        self._loser = loser

    @property
    def winner(self):
        return self._winner

    @property
    def loser(self):
        return self._loser


class Match(object):
    """A match"""

    def __init__(self, client1, client2, seed=None, display=False, config=None):
        self._clients = [client1, client2]
        self._random = random.Random(seed)
        self._display = display
        self._config = config if config is not None else Configuration()

    @property
    def random(self):
        return self._random

    def run(self):
        self._turn_num = 0
        player1 = Player(self, self._clients[0])
        player2 = Player(self, self._clients[1])
        player1.opponent = player2
        player2.opponent = player1
        if self.random.random() >= 0.5:
            player1, player2 = player2, player1
        player1.first = True
        player2.first = False
        self._players = [player1, player2]
        player1.deck.shuffle(self._random)
        player2.deck.shuffle(self._random)

        try:
            player1.draw(3)
            player2.draw(4)
            player1.replace()
            player2.replace()
            if self._config.coin:
                coin = TheCoin()
                coin.owner = player2
                player2.hand.append(coin)
                logging.info('Player <%s> obtained a card (%s)',
                             player2.name, coin.name)
            me = self._players[0]
            enemy = self._players[1]
            self.new_turn(me)
            while True:
                if self._display:
                    print enemy
                    print me
                action = me.client.decide(me, enemy)  # TODO: Add events
                if action[0] == 'play':  # Play a card
                    card_index = action[1]
                    self.play(me, enemy, card_index)
                elif action[0] == 'attack':  # Order a minion to attack
                    attacker_index = action[1]
                    attackee_index = action[2]
                    self.attack(me, enemy, attacker_index, attackee_index)
                elif action[0] == 'end':  # End this turn
                    # TODO: end of turn
                    me, enemy = enemy, me
                    self.new_turn(me)
                    # TODO: begin of turn
                elif action[0] == 'concede':  # Concede
                    raise MatchResult(enemy, me)
                else:
                    logging.warning('Invalid action: %s', action)
        except MatchResult as match_result:
            winner = match_result.winner
            loser = match_result.loser
        except:
            raise
        logging.info('Player <%s> won', winner.name)
        return (winner.client, winner.first, self._turn_num)

    def new_turn(self, me):
        self._turn_num += 1
        logging.info('Turn #%d began', self._turn_num)
        me.regenerate()
        me.draw()
        for minion in me.battlefield:
            minion.reset_attack_status()

    def play(self, me, enemy, card_index):
        card_index = int(card_index)
        if not (0 <= card_index < len(me.hand)):
            logging.warning('Invalid card index: %d', card_index)
            return
        card = me.hand[card_index]
        if not card.can_play():
            logging.warning('Cannot play card (%s)', card.name)
            return
        me.play(card)

    def attack(self, me, enemy, attacker_index, attackee_index):
        if attacker_index == 'H' or attacker_index == 'h':
            attacker = me.hero
        else:
            attacker_index = int(attacker_index)
            if not (0 <= attacker_index < len(me.battlefield)):
                logging.warning('Invalid attacker index: %d', attacker_index)
                return
            attacker = me.battlefield[attacker_index]
        if attackee_index == 'H' or attackee_index == 'h':
            attackee = enemy.hero
        else:
            attackee_index = int(attackee_index)
            if not (0 <= attackee_index < len(enemy.battlefield)):
                logging.warning('Invalid attackee index: %d', attackee_index)
                return
            attackee = enemy.battlefield[attackee_index]
        attacker.attack_(attackee)


from cards import TheCoin  # XXX: Import at the end to work around circular
