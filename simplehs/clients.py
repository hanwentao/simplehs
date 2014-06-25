# Client classes

import readline

from base import Client


class DummyClient(Client):
    """A dummy client"""
    pass


class NaiveClient(Client):
    """A naive client"""

    def decide(self, player):
        for card_index, card in enumerate(player.hand):
            if card.can_play:
                return ('play', str(card_index))
        for minion_index, minion in enumerate(player.battlefield):
            if minion.can_attack:
                return ('attack', str(minion_index), 'h')
        return ('end', )


class ClearClient(Client):
    """A naive client"""

    def decide(self, player):
        for card_index, card in enumerate(player.hand):
            if card.can_play:
                return ('play', str(card_index))
        enemy = player.opponent
        for minion_index, minion in enumerate(player.battlefield):
            if minion.can_attack:
                if len(enemy.battlefield) > 0:
                    return ('attack', str(minion_index), '0')
                else:
                    return ('attack', str(minion_index), 'h')
        return ('end', )


class ConsoleClient(Client):
    """A console client"""

    def replace(self, player):
        line = raw_input('Which cards to replace: ')
        tokens = line.split()
        index_list = [int(token) for token in tokens]
        action = ('replace', index_list)
        return action

    def decide(self, player):
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
