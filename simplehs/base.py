# Base classes

import importlib
import logging
import random


class Object(object):
    """An object"""

    def __init__(self, root, id, owner, name):
        self._root = root
        self._id = id
        self._owner = owner
        self._name = name

    def __hash__(self):
        return self._id

    @property
    def root(self):
        return self._root

    @property
    def id(self):
        return self._id

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value

    @property
    def name(self):
        return self._name


class Character(Object):
    """A character"""

    def __init__(self, root, id, owner, name, attack, health):
        super(Character, self).__init__(root, id, owner, name)
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

    @property
    def can_attack(self):
        return (self.attack > 0 and not self._sleeping and
                self._num_attacks_done < self._num_attacks_allowed)

    def reset_attack_status(self):
        self._sleeping = False
        self._num_attacks_done = 0

    def attack_(self, target):
        if not self.can_attack:
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

    def __init__(self, root, id, owner, name, health):
        super(Hero, self).__init__(root, id, owner, name, 0, health)

    def die(self):
        super(Hero, self).die()
        raise MatchResult(self.owner.opponent)


class Minion(Character):
    """A minion"""

    def __init__(self, root, id, owner, name, attack, health):
        super(Minion, self).__init__(root, id, owner, name, attack, health)
        self._sleeping = True

    def die(self):
        super(Minion, self).die()
        self.owner.battlefield.remove(self)
        self.root.remove(self)


class Weapon(Object):
    pass


class Card(Object):
    """A card"""

    def __init__(self, root, id, owner, name, cost):
        super(Card, self).__init__(root, id, owner, name)
        self._cost = cost

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    @property
    def cost(self):
        return self._cost

    @property
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

    def __init__(self, root, id, owner, name, cost, attack, health):
        super(MinionCard, self).__init__(root, id, owner, name, cost)
        self._attack = attack
        self._health = health

    @property
    def can_play(self):
        enough_mana = super(MinionCard, self).can_play
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

    def play(self):
        super(MinionCard, self).play()
        minion = self.root.create(Minion, self.owner,
                                  self.name, self.attack, self.health)
        self.owner._mana -= self.cost
        self.owner.battlefield.append(minion)
        logging.info('Player <%s> summoned a minion [%s]',
                     self.owner.name, minion.name)


class SpellCard(Card):
    """A spell card"""

    def __init__(self, root, id, owner, name, cost):
        super(SpellCard, self).__init__(root, id, owner, name, cost)


class WeaponCard(Card):
    pass


class Player(Object):
    """A player"""

    def __init__(self, root, id, owner, client, first):
        super(Player, self).__init__(root, id, owner, client.name)
        self._client = client
        self._opponent = None
        self._first = first
        self._hero = root.create(client.hero_class, self)
        self._deck = Deck()
        module_cards = importlib.import_module('simplehs.cards')
        for card_name in client.deck:
            card_class = getattr(module_cards, card_name)
            card = root.create(card_class, self)
            self._deck.append(card)
        self._deck.shuffle(root.random)
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
    def client(self):
        return self._client

    @property
    def opponent(self):
        return self._opponent

    @opponent.setter
    def opponent(self, value):
        self._opponent = value

    @property
    def first(self):
        return self._first

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
        self.deck.put_back(cards, self.root.random)

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

    def replace(self, player):
        return ('replace', [])

    def decide(self, player):
        return ('end', )


class Configuration(object):
    """Match configuration"""

    def __init__(self, *args, **kwargs):
        self._config = {}

    @property
    def seed(self):
        return self._config.get('seed', 0)

    @seed.setter
    def seed(self, value):
        self._config['seed'] = value

    @property
    def coin(self):
        return self._config.get('coin', True)

    @coin.setter
    def coin(self, value):
        self._config['coin'] = value

    @property
    def display(self):
        return self._config.get('display', False)

    @display.setter
    def display(self, value):
        self._config['display'] = value


class MatchResult(Exception):
    """Exception indicates the result of a match"""

    def __init__(self, winner):
        self._winner = winner

    @property
    def winner(self):
        return self._winner


class Match(object):
    """A match"""

    def __init__(self, client1, client2, config=None):
        self._config = config if config is not None else Configuration()
        self._client1 = client1
        self._client2 = client2
        self._random = random.Random(config.seed)
        self._objects = set()

    @property
    def random(self):
        return self._random

    def next_id(self):
        return len(self._objects)

    def create(self, class_, owner, *args, **kwargs):
        """Create an object, e.g., Card, Hero, Minion, Weapon, etc."""
        id = self.next_id()
        object = class_(self, id, owner, *args, **kwargs)
        self._objects.add(object)
        return object

    def remove(self, object):
        self._objects.remove(object)

    def run(self):
        self._turn_num = 0
        client1_is_first = self.random.randint(0, 1) == 0
        client2_is_first = not client1_is_first
        player1 = self.create(Player, None, self._client1, client1_is_first)
        player2 = self.create(Player, None, self._client2, client2_is_first)
        player1.opponent = player2
        player2.opponent = player1
        if client2_is_first:
            player1, player2 = player2, player1
        try:
            player1.draw(3)
            player2.draw(4)
            player1.replace()
            player2.replace()
            if self._config.coin:
                from cards import TheCoin
                coin = self.create(TheCoin, player2)
                player2.hand.append(coin)
                logging.info('Player <%s> obtained a card (%s)',
                             player2.name, coin.name)
            player = player1
            self.new_turn(player)
            while True:
                if self._config.display:
                    print player.opponent
                    print player
                action = player.client.decide(player)  # TODO: Add events
                if action[0] == 'play':  # Play a card
                    card_index = action[1]
                    self.play(player, card_index)
                elif action[0] == 'attack':  # Order a minion to attack
                    attacker_index = action[1]
                    attackee_index = action[2]
                    self.attack(player, attacker_index, attackee_index)
                elif action[0] == 'end':  # End this turn
                    # TODO: end of turn
                    player = player.opponent
                    self.new_turn(player)
                    # TODO: begin of turn
                elif action[0] == 'concede':  # Concede
                    raise MatchResult(player.opponent)
                else:
                    logging.warning('Invalid action: %s', action)
        except MatchResult as match_result:
            winner = match_result.winner
        except:
            raise
        logging.info('Player <%s> won', winner.name)
        return (winner.client, winner.first, self._turn_num)

    def new_turn(self, player):
        self._turn_num += 1
        logging.info('Turn #%d began', self._turn_num)
        player.regenerate()
        player.draw()
        for minion in player.battlefield:
            minion.reset_attack_status()

    def play(self, player, card_index):
        card_index = int(card_index)
        if not (0 <= card_index < len(player.hand)):
            logging.warning('Invalid card index: %d', card_index)
            return
        card = player.hand[card_index]
        if not card.can_play:
            logging.warning('Cannot play card (%s)', card.name)
            return
        player.play(card)

    def attack(self, player, attacker_index, attackee_index):
        if attacker_index == 'H' or attacker_index == 'h':
            attacker = player.hero
        else:
            attacker_index = int(attacker_index)
            if not (0 <= attacker_index < len(player.battlefield)):
                logging.warning('Invalid attacker index: %d', attacker_index)
                return
            attacker = player.battlefield[attacker_index]
        enemy = player.opponent
        if attackee_index == 'H' or attackee_index == 'h':
            attackee = enemy.hero
        else:
            attackee_index = int(attackee_index)
            if not (0 <= attackee_index < len(enemy.battlefield)):
                logging.warning('Invalid attackee index: %d', attackee_index)
                return
            attackee = enemy.battlefield[attackee_index]
        attacker.attack_(attackee)
