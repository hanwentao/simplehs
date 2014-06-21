# Client classes

import sys

from base import Client


class ConsoleClient(Client):
    """A console client"""

    def __init__(self, name, hero_class, deck):
        Client.__init__(self, name, hero_class, deck)

    def decide(self, me, enemy):
        while True:
            sys.stdout.write('Enter an action: ')
            sys.stdout.flush()
            line = sys.stdin.readline()
            tokens = line.split()
            if len(tokens) == 0:
                sys.stdout.write('ERROR: Empty action\n')
                sys.stdout.flush()
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
                sys.stdout.write('ERROR: Unknown action\n')
                sys.stdout.flush()
        return action
