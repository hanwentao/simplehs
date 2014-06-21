# Client classes

import readline

from base import Client


class DummyClient(Client):
    """A dummy client"""

    def decide(self, me, enemy):
        return ('end', )


class NaiveClient(Client):
    """A naive client"""

    def decide(self, me, enemy):
        for card_index, card in enumerate(me.hand):
            if card.cost <= me.mana:
                return ('play', str(card_index))
        for minion_index, minion in enumerate(me.battlefield):
            if minion.can_attack:
                return ('attack', str(minion_index), 'h')
        return ('end', )


class ConsoleClient(Client):
    """A console client"""

    def decide(self, me, enemy):
        while True:
            line = raw_input('Enter an action: ')
            tokens = line.split()
            if len(tokens) == 0:
                print 'ERROR: Empty action'
                continue
            if tokens[0] == 'play':
                action = ('play', tokens[1])
                break
            elif tokens[0] == 'attack':
                action = ('attack', tokens[1], tokens[2])
                break
            elif tokens[0] == 'end':
                action = ('end', )
                break
            elif tokens[0] == 'concede':
                action = ('concede', )
                break
            else:
                print 'ERROR: Unknown action'
        return action