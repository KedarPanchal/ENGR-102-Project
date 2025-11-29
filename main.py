from game.player import Player


# using file methods to display the rules of the game
def displayrules():
    '''Read and display the file with Flip 7 rules for players'''
    rules = open('Flip7Rules.txt', 'r')
    rules_text = rules.read()
    print(rules_text)


def startround(players):
    '''Each player decides if they want to hit or stay and runs through the round'''
    listofplayers = []
    for i in range(players):
        listofplayers += Player(i)
    currentplayernum = 1
    game = True
    while (game):
        currentplayer = listofplayers[currentplayernum - 1]
        choice = input(f"Player {currentplayernum}, would you like to hit or pass?")
        if (choice.lower() == "hit"):
            currentplayer.hit()
        elif (choice.lower() == "pass"):
            currentplayer.stay()

        if currentplayer.has_seven() or currentplayer.is_busted():
            game = False

        currentplayernum += 1
        if (currentplayernum > players):
            currentplayernum = 1


def calculatescore():
    pass


displayrules()

# Make sure the player count is within 3-18
player_count = int(input("Enter the number of players: "))
while player_count < 3 or player_count > 18:
    player_count = int(input("Invalid player count (must be 3-18). Enter new player count: "))
