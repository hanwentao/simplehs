# Base classes

import logging


class Character(object):
    """A character"""

    def __init__(self, name, attack, health):
        self._name = name
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
    def name(self):
        return self._name

    @property
    def attack(self):
        return self._base_attack

    @property
    def health(self):
        return self._base_health

    def reset_attack_status(self):
        self._sleeping = False
        self._num_attacks_done = 0

    def attack_(self, target):
        if self._sleeping:
            logging.error('Cannot attack: sleeping')
            return
        if self._num_attacks_done >= self._num_attacks_allowed:
            logging.error('Cannot attack anymore: %d >= %d',
                          self._num_attacks_done, self._num_attacks_allowed)
            return
        logging.info('Character [%s] attacked character [%s]',
                     self.name, target.name)
        self._num_attacks_done += 1
        target.take_damage(self.attack)
        self.take_damage(target.attack)

    def take_damage(self, damage):
        logging.info('Character [%s] took %d damage', self.name, damage)
        self._base_health -= damage
        if self._base_health <= 0:
            self.die()

    def die(self):
        logging.info('Character [%s] died', self.name)


class Hero(Character):
    """A hero"""

    def __init__(self, name, health):
        Character.__init__(self, name, 0, health)


class Minion(Character):
    """A minion"""

    def __init__(self, name, attack, health):
        Character.__init__(self, name, attack, health)
        self._owner = None
        self._sleeping = True

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value

    def die(self):
        Character.die(self)
        self._owner.battlefield.remove(self)


class Weapon(object):
    pass


class Card(object):
    """A card"""

    def __init__(self, name, cost):
        self._name = name
        self._cost = cost

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    @property
    def name(self):
        return self._name

    @property
    def cost(self):
        return self._cost


class MinionCard(Card):
    """A minion card"""

    def __init__(self, name, cost, attack, health):
        Card.__init__(self, name, cost)
        self._attack = attack
        self._health = health

    @property
    def attack(self):
        return self._attack

    @property
    def health(self):
        return self._health

    def summon_minion(self):
        return Minion(self.name, self.attack, self.health)


class SpellCard(Card):
    pass


class WeaponCard(Card):
    pass


class Player(object):
    """A player"""

    def __init__(self, client):
        self._client = client
        self._name = client.name
        self._hero = client.hero_class()
        self._deck = client.deck[:]
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
                    self.deck))

    @property
    def client(self):
        return self._client

    @property
    def name(self):
        return self._name

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
        self._full_mana = min(self._full_mana + 1, 10)
        self._mana = self._full_mana
        logging.info('Player <%s> regenerated %d mana', self.name, self.mana)

    def draw(self, num_cards=1):
        for card_num in xrange(num_cards):
            # TODO: Check for fatigue
            card = self.deck.pop(0)
            self.hand.append(card)
            logging.info('Player <%s> drew a card (%s)', self.name, card.name)


class Deck(list):
    pass


class Hand(list):
    pass


class Battlefield(list):
    pass


class Client(object):
    """A Hearthstone client represents a player."""

    def __init__(self, name, hero_class, deck):
        self._name = name
        self._hero_class = hero_class
        self._deck = deck

    @property
    def name(self):
        return self._name

    @property
    def hero_class(self):
        return self._hero_class

    @property
    def deck(self):
        return self._deck

    def decide(self, me, enemy):
        pass


class Match(object):
    """A match"""

    def __init__(self, client1, client2):
        self._clients = [client1, client2]

    def run(self):
        self._turn_num = 0
        player1 = Player(self._clients[0])
        player2 = Player(self._clients[1])
        self._players = [player1, player2]
        player1.draw(3)
        player2.draw(4)
        # TODO: Add The Coin
        me = self._players[0]
        enemy = self._players[1]
        self.new_turn(me)
        while True:
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
                winner = enemy
                loser = me
                break
            else:
                logging.error('Invalid action: %s', action)
            if me.hero.health <= 0:
                winner = enemy
                loser = me
                break
            if enemy.hero.health <= 0:
                winner = me
                loser = enemy
                break
        logging.info('Player <%s> won', winner.name)

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
            logging.error('Invalid card index: %d', card_index)
            return
        card = me.hand[card_index]
        if card.cost > me.mana:
            logging.error('Not enough mana: %d < %d', me.mana, card.cost)
            return
        me.hand.pop(card_index)
        minion = card.summon_minion()
        me._mana -= card.cost
        me.battlefield.append(minion)
        minion.owner = me
        logging.info('Player <%s> played a card (%s) to summon a minion [%s]',
                     me.name, card.name, minion.name)

    def attack(self, me, enemy, attacker_index, attackee_index):
        if attacker_index == 'H' or attacker_index == 'h':
            attacker = me.hero
        else:
            attacker_index = int(attacker_index)
            if not (0 <= attacker_index < len(me.battlefield)):
                logging.error('Invalid attacker index: %d', attacker_index)
                return
            attacker = me.battlefield[attacker_index]
        if attackee_index == 'H' or attackee_index == 'h':
            attackee = enemy.hero
        else:
            attackee_index = int(attackee_index)
            if not (0 <= attackee_index < len(enemy.battlefield)):
                logging.error('Invalid attackee index: %d', attackee_index)
                return
            attackee = enemy.battlefield[attackee_index]
        attacker.attack_(attackee)
