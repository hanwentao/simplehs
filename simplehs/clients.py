# Client classes

import readline

from base import Client


class ConsoleClient(Client):
    """A console client"""

    def __init__(self, name, hero_class, deck):
        Client.__init__(self, name, hero_class, deck)

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
