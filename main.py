import sys
import subprocess
import importlib.metadata as metadata


# Dynamically install a pip package
def install(package: str) -> None:
    """Dynamically installs a pip package if not already installed.
    If installation fails, prompts the user to install manually.
    Args:
        package: The name of the package to install.
    """
    print(f"Checking for package: {package}")
    for distribution in metadata.distributions():
        if distribution.metadata['Name'] == package:
            print(f"Package {package} is already installed.")
            return

    print(f"Package {package} not found. Installing...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to install package {package}: {e}")
        print(f"Please install the package {package} manually and re-run the program.")
        print(f"Installation command: {sys.executable} -m pip install {package}")
        sys.exit(1)


install("PyTermGUI")
install("keyboard")

import asyncio

from game.player import Player
from game.deck import Deck
from tui.ui import UI


# using file methods to display the rules of the game
def displayrules():
    '''Read and display the file with Flip 7 rules for players'''
    rules = open('Flip7Rules.txt', 'r')
    rules_text = rules.read()
    rules.close()
    return rules_text


def checkRoundEnd(playerdict):
    for i in range(1, len(playerdict) + 1):
        if playerdict[i].is_active():
            return False
        if playerdict[i].has_seven():
            return True
    return True


async def main():
    # Initialize async variables
    ui = UI()
    asyncio.create_task(ui.run())
    await ui.wait_until_running()

    # Main code goes here
    await ui.println(displayrules())
    await ui.println("Press Enter to start the game...")
    await ui.input()
    await ui.clear()

    # Make sure player count in between 3-18 players
    await ui.println("Enter the number of players (3-18): ")
    player_count = await ui.input()

    # Validate player count input
    while True:
        try:
            player_count = int(player_count)
            if player_count < 3 or player_count > 18:
                await ui.println("Invalid player count (must be 3-18). Try again: ")
                player_count = await ui.input()
            else:
                break
        except ValueError:
            await ui.println("Invalid player count. Must be an Integer. Try again: ")
            player_count = await ui.input()

    # Create Dictionary for Player list
    playerids = {}
    for i in range(1, player_count + 1):
        playerids[i] = Player(i)
        playerids[i].set_callbacks(ui.println, ui.input)

    # Set opponents for each Player object
    for i in range(1, player_count + 1):
        playerids[i].set_players(playerids.values())

    # Initialize deck and discard pile
    deck = Deck()
    deck.shuffle()
    discard_pile = []

    # Start Game
    currentplayerid = 0
    game = True
    while game:
        # Loop back to player 1 if player id is greater player count
        if currentplayerid >= player_count:
            currentplayerid = 1
        else:
            currentplayerid += 1

        # Skip player if player has already busted
        if not playerids[currentplayerid].is_active():
            continue

        # Print hand
        await ui.clear(window="hand")
        await ui.println(f"Score: {playerids[currentplayerid].get_score()}", window="hand")
        for card in playerids[currentplayerid]:
            await ui.println(card, window="hand")
        # Ask player their choice for turn
        await ui.println(f"Player {currentplayerid}, would you like to hit, stay or end game")
        decision = await ui.input()

        # If player chose to hit
        if decision.lower() == "hit":
            card_drawn = await playerids[currentplayerid].hit(deck)
            if not card_drawn:
                # Check if deck is empty
                if len(deck) == 0:
                    deck.return_cards(discard_pile)
                    deck.shuffle()
                    await ui.println("Deck was empty. Discard pile shuffled")
                    currentplayerid -= 1  # redo turn for current player
                    continue

        # If player chose to stay
        elif decision.lower() == "stay":
            await ui.println(f"Player {currentplayerid} stood and their round is over.")
            playerids[currentplayerid].stay()

        # If player wants to end game
        elif decision.lower() == "end" or decision.lower() == "endgame" or decision.lower() == "end game":
            game = False
            break

        else:
            # If player did not hit, stay, or end the game
            await ui.println("Invalid decision. Try again: ")
            currentplayerid -= 1  # redo turn for current player
            continue

        # Check if each player busted then see if they have a second chance to stay in the round
        if playerids[currentplayerid].is_busted():
            if playerids[currentplayerid].has_second_chance():
                playerids[currentplayerid].use_second_chance()
                await ui.println(f"Player {currentplayerid} busted and used second chance.")
            else:
                await ui.println(f"Player {currentplayerid} busted and their round is over.")
                playerids[currentplayerid].stay()

        # Check if round is over and add scores
        if checkRoundEnd(playerids):
            await ui.println("Round over! Calculating scores...")
            for playerid in playerids:
                playerids[playerid].update_score()
                playerids[playerid].reset()
                playerids[playerid].add_bonus()  # Only adds bonus if player meets the criteria

            # Reset state for next round
            currentplayerid = 0
            await ui.println("\n")

            # Check if any player has won the game
            for playerid in playerids:
                if (playerids[playerid].won_game()):
                    game = False

    await ui.stop()

if __name__ == "__main__":
    asyncio.run(main())
