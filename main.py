from game.player import Player


# using file methods to display the rules of the game
def displayrules():
    '''Read and display the file with Flip 7 rules for players'''
    rules = open('Flip7Rules.txt', 'r')
    rules_text = rules.read()
    print(rules_text)
