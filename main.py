import asyncio

from game.card import ActionCard, NumberCard, ScoreModifierCard
from game.player import Player
from game.deck import Deck
from tui.ui import UI


# using file methods to display the rules of the game
def displayrules():
    """Read and display the file with Flip 7 rules for players.
    Ensure that Flip7Rules.txt is in the same directory as main.py.
     Returns:
         The text of the rules as a string.
     """
    rules = open('Flip7Rules.txt', 'r')
    rules_text = rules.read()
    rules.close()
    return rules_text


def checkRoundEnd(playerdict):
    """Check if the current round has ended.
    A round ends when all players have either busted or chosen to stay,
    or if any player has seven unique number cards in hand.
    Args:
        playerdict: Dictionary of Player objects keyed by player ID.
    Returns:
        True if the round has ended, False otherwise.
    """
    for i in range(1, len(playerdict) + 1):
        if playerdict[i].is_active():
            return False
        if playerdict[i].has_seven():
            return True
    return True


async def main():
    """The main function to run the Flip 7 game.
    Initializes the UI as a background coroutine and manages the game flow.
    This function should be run in an asynchronous event loop.
    """
    # Initialize async variables
    ui = UI()
    asyncio.create_task(ui.run())
    await ui.wait_until_running()

    # Main code goes here
    await ui.println(displayrules())
    await ui.println("\nPress Enter to start the game...")
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
    round = 1
    winner = False
    while not winner:
        # Loop back to player 1 if player id is greater player count
        if currentplayerid >= player_count:
            currentplayerid = 1
        else:
            currentplayerid += 1

        # Skip player if player has already busted
        if not playerids[currentplayerid].is_active():
            continue

        # Update round count in main window
        await ui.set_title(f"Flip 7 - Round {round}", fmt="210 bold")

        # Print hand and current player metadata
        await ui.clear(window="hand")
        await ui.println(
            "Score:", playerids[currentplayerid].get_score(),
            fmts=["green bold", "#ffffff"],
            window="hand"
        )
        await ui.println(
            "Second Chance Available:", playerids[currentplayerid].has_second_chance(), 
            fmts=["magenta bold", "#ffffff"],
            window="hand"
        )
        await ui.println("Modifier Cards:", fmts=["yellow bold"], window="hand")
        for card in playerids[currentplayerid]:
            if isinstance(card, ScoreModifierCard):
                await ui.println(card, window="hand")
        await ui.println("Number Cards", fmts=["yellow bold"], window="hand")
        for card in playerids[currentplayerid]:
            if isinstance(card, NumberCard):
                await ui.println(card, window="hand")
        await ui.println("Action Cards:", fmts=["yellow bold"], window="hand")
        for card in playerids[currentplayerid]:
            if isinstance(card, ActionCard):
                await ui.println(card, window="hand")

        # Set hand window title
        await ui.set_title(f"Player {currentplayerid}'s Info", fmt="210 bold", window="hand")

        # Ask player their choice for turn
        await ui.println(
            f"Player {currentplayerid},",
            "what is your decision? (hit/stay/end):",
            fmts=["cyan bold", "#ffffff"]
        )
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
            await ui.println(
                f"Player {currentplayerid}", "stood and their round is over.",
                fmts=["cyan bold", "#ffffff"]
            )
            playerids[currentplayerid].stay()

        # If player wants to end game
        elif decision.lower() == "end" or decision.lower() == "endgame" or decision.lower() == "end game":
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
                await ui.println(
                    f"Player {currentplayerid}", "busted and used a second chance.",
                    fmts=["cyan bold", "#ffffff"]
                )
            else:
                await ui.println(
                    f"Player {currentplayerid}", "busted and their round is over.",
                    fmts=["cyan bold", "#ffffff"]
                )
                playerids[currentplayerid].stay()

        # Check if round is over and add scores
        if checkRoundEnd(playerids):
            await ui.println("Round over! Calculating scores...")
            for playerid in playerids:
                playerids[playerid].update_score()
                playerids[playerid].reset()
                if playerids[playerid].has_seven() and not playerids[playerid].is_busted():
                    await ui.println(
                        f"Player {currentplayerid}", "is a round winner and receives bonus points!",
                        fmts=["cyan bold", "#ffffff"]
                    )
                playerids[playerid].add_bonus()  # Only adds bonus if player meets the criteria

            # Set state for next round
            currentplayerid = 0
            round += 1
            await ui.clear()

            # Check if any player has won the game
            for playerid in playerids:
                if (playerids[playerid].won_game()):
                    winner = True
                    break

    await ui.clear()

    rankings = sorted(playerids.values(), key=lambda p: p.get_score(), reverse=True)
    # Game ended early without a winner
    if not winner:
        await ui.println(
            "Game ended early.", "No winner.",
            fmts=["#ffffff", "red bold"]
         )
    elif rankings[0] != rankings[1]: # Only one winner
        await ui.println(
            f"Player {rankings[0].get_id()}", "has won the game with a score of", rankings[0].get_score(),
            fmts=["green bold", "#ffffff", "green bold"]
        )
    else:  # Multiple players tied for first place
        top_score = rankings[0].get_score()
        winners = [player for player in rankings if player.get_score() == top_score]
        winner_ids = ', '.join(str(player.get_id()) for player in winners)
        await ui.println(
            f"Players {winner_ids}", "have tied for first place with a score of", top_score,
            fmts=["cyan bold", "#ffffff", "green bold"]
        )
    
    await ui.println("\nFinal Rankings:")
    for rank, player in enumerate(rankings, start=1):
        await ui.println(
                f"{rank}.", f"Player {player.get_id()}", "-", f"Score: {player.get_score()}",
            fmts=["210 bold", "cyan bold", "#ffffff", "green bold"]
        )
    await ui.println("\nPress Enter to exit...")
    await ui.input()
    await ui.stop()

if __name__ == "__main__":
    asyncio.run(main())
