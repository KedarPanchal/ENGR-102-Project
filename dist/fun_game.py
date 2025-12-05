# By submitting this assignment, I agree to the following:
# "Aggies do not lie, cheat, or steal, or tolerate those who do."
# "I have not given or received any unauthorized aid on this assignment."
#
# Names: Kedar Panchal
# Blane Weiblen
# Nate Waguespack
# Joshua Le
# Section: 213
# Assignment: Lab 13
# Date: 5 December 2025
#
#

"""
Flip 7 Game - Consolidated Version
All game logic, UI, and main code in a single file.
"""

import asyncio
import io
import keyboard
import pytermgui as ptg
import random
from abc import ABC, abstractmethod
from typing import List, Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


# ============================================================================
# CARD CLASSES
# ============================================================================

class BaseCard(ABC):
    """Abstract base class for all card types in the Flip Seven game.

    This class serves as the foundation for all card implementations,
    ensuring a consistent interface across different card types.
    """

    @abstractmethod
    def __str__(self) -> str:
        """Provide a string representation of the card."""
        return ""


class AddableCard(BaseCard):
    """Abstract class for cards that have numeric values.

    This class defines the interface for cards that have a numeric value
    that can be used in score calculations.

    Attributes:
        _value: The numeric value of the card.
    """

    def __init__(self, value: int):
        """Initialize an AddableCard with a specific value.

        Args:
            value: The numeric value for this card.
        """
        self._value = value

    def value(self) -> int:
        """Get the numeric value of the card.

        Returns:
            The card's numeric value.
        """
        return self._value

    def __str__(self) -> str:
        """Provide a string representation of the card.

        Returns:
            A string showing the card's value.
        """
        return f"{self._value}"


class NumberCard(AddableCard):
    """Represents a numbered card in the Flip Seven game.

    Number cards have a numeric value and can be compared for equality.
    Players collect sets of unique number cards to achieve victory.
    Players must collect exactly seven unique number cards without duplicates.
    """

    def __hash__(self) -> int:
        """Compute hash based on the card's value.

        Returns:
            Hash value of the card.
        """
        return hash(self._value)

    def __eq__(self, other: object) -> bool:
        """Check equality with another card.

        Args:
            other: Another object to compare with.

        Returns:
            True if both are NumberCards with the same value, False otherwise.
        """
        if isinstance(other, NumberCard):
            return self._value == other._value
        return False


class ScoreModifierCard(AddableCard):
    """Represents a card that modifies player scores.

    These cards affect the scoring mechanism of the game when played.
    They can either add to or multiply the player's score.

    Attributes:
        _value: The modifier value (inherited from AddableCard).
        _is_addition: Whether this card adds (True) or multiplies (False).
    """

    def __init__(self, modifier: int, is_addition: bool):
        """Initialize a ScoreModifierCard with a specific modifier.

        Args:
            modifier: The score modification value.
            is_addition: True if this card adds to score, False if it multiplies.
        """
        super().__init__(modifier)
        self._is_addition = is_addition

    def is_addition(self) -> bool:
        """Check if the card is an addition modifier.

        Returns:
            True if the card adds to the score, False if it multiplies.
        """
        return self._is_addition

    def __str__(self) -> str:
        """Provide a string representation of the score modifier card.

        Returns:
            A string showing the modifier type and value.
        """
        return f"{'+' if self._is_addition else 'x'}{self._value}"


class ActionCard(BaseCard):
    """Represents a card that triggers special actions when drawn.

    Action cards provide special game effects that target players.
    Subclasses must implement the action method to define behavior.
    """

    @abstractmethod
    async def action(self, targeted_player: 'Player') -> None:
        """Perform the action associated with this card.

        Args:
            targeted_player: The player affected by the action.
        """
        pass

    async def _print(self, *args, fmts: Optional[List[str]]=None, sep=" ", targeted_player: 'Player') -> None:
        """Print a message to the targeted player's print callback.

        Args:
            message: The message to print.
            targeted_player: The player whose print callback will be used.
        """
        if targeted_player._print:
            await targeted_player._print(*args, fmts=fmts, sep=sep)


class FreezeCard(ActionCard):
    """Represents a Freeze action card that skips a player's next turn."""

    async def action(self, targeted_player: 'Player') -> None:
        """Skip the targeted player's next turn.

        Args:
            targeted_player: The player to be frozen.
        """
        targeted_player.stay()
        await self._print(
            f"Player {targeted_player.get_id()}", "has been frozen and will skip their next turn!",
            fmts=["cyan bold", "#ffffff"],
            targeted_player=targeted_player
        )

    def __str__(self) -> str:
        """Provide a string representation of the Freeze card.

        Returns:
            A string indicating this is a Freeze card.
        """
        return "Freeze!"


class SecondChanceCard(ActionCard):
    """Represents a Second Chance action card that allows a player to draw again."""

    async def action(self, targeted_player: 'Player') -> None:
        """Allow the targeted player to draw another card.

        Args:
            targeted_player: The player who gets a second chance.
        """
        targeted_player.add_second_chance()
        await self._print(
            f"Player {targeted_player.get_id()}", "has received a Second Chance!",
            fmts=["cyan bold", "#ffffff"],
            targeted_player=targeted_player
        )

    def __str__(self) -> str:
        """Provide a string representation of the Second Chance card.

        Returns:
            A string indicating this is a Second Chance card.
        """
        return "Second Chance!"


class FlipThreeCard(ActionCard):
    def __init__(self, deck: 'Deck') -> None:
        """Initialize a Flip Three action card with a reference to the deck.
        Args:
            deck: The deck from which cards will be drawn.
        """
        self._deck = deck

    async def action(self, targeted_player: 'Player') -> None:
        """Force the targeted player to flip three cards.

        Args:
            targeted_player: The player who must flip three cards.
        """
        action_card_stack = []
        for _ in range(3):
            card = self._deck.take_card()
            # Stop if the deck is empty
            if not card:
                break
            # Handle action cards separately
            if isinstance(card, ActionCard):
                action_card_stack.append(card)
            else:
                targeted_player.receive_card(card)
                if targeted_player.is_busted():
                    if targeted_player.has_second_chance():
                        await self._print(
                            f"Player {targeted_player.get_id()}", "busted and used a second chance.",
                            fmts=["cyan bold", "#ffffff"],
                            targeted_player=targeted_player
                        )
                        targeted_player.use_second_chance()
                    else:
                        await self._print(
                            f"Player {targeted_player.get_id()}", "busted and their round is over.",
                            fmts=["cyan bold", "#ffffff"],
                            targeted_player=targeted_player
                        )
                        targeted_player.stay()
                        break
                if targeted_player.has_seven():
                    break

        # Execute any action cards drawn
        while action_card_stack:
            action_card = action_card_stack.pop()
            await self._print(
                f"Player {targeted_player.get_id()}", "flipped the card", f"{action_card}",
                fmts=["cyan bold", "#ffffff", "yellow bold"],
                targeted_player=targeted_player
            )
            await targeted_player.take_action(action_card)

    def __str__(self) -> str:
        """Provide a string representation of the Flip Three card.

        Returns:
            A string indicating this is a Flip Three card.
        """
        return "Flip Three!"


# ============================================================================
# DECK CLASS
# ============================================================================

class Deck:
    """Manages a collection of cards for the Flip Seven game.

    The deck holds cards that can be shuffled and drawn by players.

    Attributes:
        cards: List of cards in the deck.
    """

    def __init__(self):
        """Initialize a deck with all cards for the Flip Seven game.

        Creates and adds the following cards to the deck:
        - NumberCards: 12 twelves, 11 elevens, 10 tens, down to 1 one, plus 1 zero
        - ScoreModifierCards: One each of +2 through +10, and one x2 multiplier
        - ActionCards: To be added when their implementation is complete
        """
        self._cards: List[BaseCard] = []
        # Add NumberCards
        for number in range(1, 13):
            for _ in range(number):
                self._cards.append(NumberCard(number))
        self._cards.append(NumberCard(0))
        # Add ScoreModifierCards
        for i in range(2, 11):
            self._cards.append(ScoreModifierCard(i, True))
        for i in range(6):
            self._cards.append(ScoreModifierCard(2, False))
        # Add ActionCards
        for _ in range(4):
            self._cards.append(FreezeCard())
            self._cards.append(SecondChanceCard())
            self._cards.append(FlipThreeCard(self))

    def shuffle(self) -> None:
        """Randomly shuffle the cards in the deck."""
        random.shuffle(self._cards)

    def take_card(self) -> BaseCard | None:
        """Draw a card from the top of the deck.

        Returns:
            The top card from the deck, or None if the deck is empty.
        """
        return self._cards.pop() if self._cards else None

    def return_cards(self, cards: List[BaseCard]) -> None:
        """Return a list of cards back to the deck and clear the input list.

        Args:
            cards: List of cards to return to the deck.
        """
        self._cards += cards
        cards.clear()

    def __iter__(self) -> Iterator[BaseCard]:
        """Provide an iterator over the cards in the deck.

        Returns:
            An iterator for the deck's cards.
        """
        return iter(self._cards)

    def __len__(self) -> int:
        """Get the number of cards currently in the deck.

        Returns:
            The count of cards in the deck.
        """
        return len(self._cards)

    def __str__(self) -> str:
        """Provide a string representation of the deck.

        Returns:
            A string listing all cards in the deck.
        """
        return " ".join([str(card) for card in self._cards])


# ============================================================================
# PLAYER CLASS
# ============================================================================

class Player:
    """Represents a player in the Flip Seven game.

    Each player has a unique ID, score, and hand of cards. Players can
    draw cards, check for winning conditions, and manage their score.

    Attributes:
        id: Unique identifier for the player.
        _score: Current score of the player (private attribute).
        hand: List of cards currently held by the player.
        active: Whether the player is still active in the current round.
    """

    def __init__(self, id: int):
        """Initialize a new player.

        Args:
            id: Unique identifier for this player.
        """
        self._id = id
        self._score = 0
        self._hand: List[BaseCard] = []
        self._active = True
        self._players = []
        self._second_chance = False

        # UI callbacks
        self._print = None
        self._input = None

    def set_players(self, players) -> None:
        """Set the list of opponent players.

        Args:
            players: List of other Player instances in the game.
        """
        self._players = [player for player in players]

    def set_callbacks(self, print_, input_) -> None:
        """Set the print and input callback functions for the player.

        Args:
            print_: Function to print messages to the player.
            input_: Function to get input from the player.
        """
        self._print = print_
        self._input = input_

    def get_id(self) -> int:
        """Get the player's unique identifier.

        Returns:
            The player's ID.
        """
        return self._id

    def is_active(self) -> bool:
        """Check if the player is still active in the current round.

        Returns:
            True if the player is active, False otherwise.
        """
        return self._active

    async def hit(self, deck: Deck) -> bool | BaseCard:
        """Draw a card from the deck and add it to the player's hand.

        If the drawn card is an ActionCard, its action is immediately executed.
        The player must be active to draw cards.

        Args:
            deck: The deck to draw a card from.

        Returns:
            True if a card was successfully drawn, False otherwise.
        """
        if not self._active or not self._print:
            return False

        card = deck.take_card()
        if not card:
            return False

        self._hand.append(card)
        await self._print(
            f"Player {self._id}", "drew the card", f"{card}",
            fmts=["cyan bold", "#ffffff", "yellow bold"]
        )

        if isinstance(card, ActionCard):
            await self.take_action(card)

        return card

    async def take_action(self, action_card: ActionCard) -> None:
        """Execute the action of an ActionCard on this player.

        Args:
            action_card: The ActionCard to be executed.
        """
        if not self._print or not self._input:
            return

        targeted_player = None
        while True:
            await self._print("Select a player to target with the action card:")
            targeted_id = await self._input()
            if not targeted_id.isdigit():
                await self._print("Invalid input. Please enter a numeric player ID.")
                continue

            targeted_id = int(targeted_id)
            targeted_player = None
            for player in self._players:
                if int(player.get_id()) == targeted_id:
                    targeted_player = player
                    break

            if not targeted_player:
                await self._print(f"No player found with ID {targeted_id}. Please try again.")
                continue
            if not targeted_player.is_active():
                await self._print(f"Player {targeted_id} is not active. Please choose another player.")
                continue
            else:
                break

        await action_card.action(targeted_player)

    def stay(self) -> None:
        """End the player's turn and finalize their score for the round.

        Marks the player as inactive and calculates their final score
        based on the cards in their hand.
        """
        self._active = False

    def is_busted(self) -> bool:
        """Check if the player has duplicate number cards (bust condition).

        Returns:
            True if the player has duplicate NumberCards, False otherwise.
        """
        number_cards = [card for card in self._hand if isinstance(card, NumberCard)]
        return not self._second_chance and (len(number_cards) != len((set(number_cards))))

    def has_seven(self) -> bool:
        """Check if the player has exactly seven unique number cards.

        Returns:
            True if the player has seven unique NumberCards, False otherwise.
        """
        return len({card for card in self._hand if isinstance(card, NumberCard)}) == 7

    def get_score(self) -> int:
        """Get the player's current score.

        Returns:
            The player's score.
        """
        return self._score

    def add_bonus(self) -> None:
        """Add a bonus to the player's score if they have seven unique cards.

        Awards 15 bonus points if the player has exactly seven unique number
        cards without duplicates.
        """
        if self.has_seven() and not self.is_busted():
            self._score += 15

    def update_score(self) -> None:
        """Calculate and update the player's score based on cards in hand.
        If the player is busted, their score remains unchanged.

        Applies all score modifiers (multipliers first, then additions) and
        adds the values of all number cards to calculate the final score.
        """
        if self.is_busted():
            return

        total_multiplier = 1
        total_addition = 0
        for card in self._hand:
            if not isinstance(card, AddableCard):
                continue
            if isinstance(card, ScoreModifierCard) and not card.is_addition():
                total_multiplier *= card.value()
            else:
                total_addition += card.value()

        self._score *= total_multiplier
        self._score += total_addition

    def reset(self) -> List[BaseCard]:
        """Reset the player's state for a new round.

        Returns:
            The list of cards that were in the player's hand.
        """
        self._active = True
        self._second_chance = False
        discarded_hand = self._hand[:]
        self._hand = []
        return discarded_hand

    def has_second_chance(self) -> bool:
        """Check if the player has a second chance available.

        Returns:
            True if the player has a second chance, False otherwise.
        """
        return self._second_chance

    def add_second_chance(self) -> None:
        """Grant the player a second chance to avoid busting."""
        self._second_chance = True

    def use_second_chance(self) -> None:
        """Consume the player's second chance."""
        self._second_chance = False
        other_cards = [card for card in self._hand if not isinstance(card, NumberCard)]
        number_cards_nodupe = list({card for card in self._hand if isinstance(card, NumberCard)})
        self._hand = other_cards + number_cards_nodupe

    def receive_card(self, card: BaseCard) -> None:
        """Add a card to the player's hand.

        Args:
            card: The card to be added to the player's hand.
        """
        self._hand.append(card)

    def won_game(self) -> bool:
        """Check if the player has won the game.

        Returns:
            True if the player's score is 200 or higher, False otherwise.
        """
        return self._score >= 200

    def __iter__(self) -> Iterator[BaseCard]:
        """Allow iteration over the player's hand of cards.

        Returns:
            Iterator over the cards in the player's hand.
        """
        return iter(self._hand)

    def __str__(self) -> str:
        """Provide a string representation of the player.

        Returns:
            A string showing the player's ID and current score.
        """
        ret_str = f"Player {self._id} Score: {self._score}\nHand: "
        ret_str += " ".join([str(card) for card in self._hand])

        return ret_str.strip()


# ============================================================================
# UI CLASS
# ============================================================================

class UI:
    """Manages the terminal user interface for the Flip Seven game.

    Provides a pytermgui-based terminal interface with multiple windows
    for displaying game information, player hands, and accepting user input.
    Handles asynchronous initialization and cleanup of the UI manager.

    Attributes:
        _manager: The pytermgui WindowManager instance.
        _layout: The layout manager for arranging windows.
        _input_field: The input field for user commands.
        _input_window: The window containing the input field.
        _manager_process: The asyncio task running the UI manager.
    """

    def __init__(self):
        """Initialize the UI with windows and layout configuration.

        Creates a WindowManager with three slots:
        - main: Displays game information
        - hand: Shows the current player's hand (30% width)
        - input: Accepts user commands (height of 5)
        """
        # Initialize class variables
        self._manager = ptg.WindowManager()
        self._layout = self._manager.layout

        # Initialize layout
        self._layout.add_slot("main")
        self._layout.add_slot("hand", width=0.3)
        self._layout.add_break()
        self._layout.add_slot("input", height=5)

        # Initialize windows
        self._main_window = ptg.Window(
            title="[210 bold]Game Info",
            overflow=ptg.Overflow.SCROLL,
            vertical_align=ptg.VerticalAlignment.TOP
        )
        self._main_text = ptg.Label("", parent_align=ptg.HorizontalAlignment.LEFT)
        self._main_window += self._main_text
        self._hand_window = ptg.Window(
            title="[210 bold] Current Player's Info", 
            overflow=ptg.Overflow.SCROLL,
            vertical_align=ptg.VerticalAlignment.TOP
        )
        self._hand_text = ptg.Label("", parent_align=ptg.HorizontalAlignment.LEFT)
        self._hand_window += self._hand_text
        self._input_field = ptg.InputField(prompt="> ")
        self._input_window = ptg.Window(self._input_field)

        # Add windows
        self._manager.add(self._main_window, assign="main")
        self._manager.add(self._hand_window, assign="hand")
        self._manager.add(self._input_window, assign="input")

        # Input handling
        self._input_field.bind(ptg.keys.ENTER, self._handle_input)
        self._input_field.bind(ptg.keys.RETURN, self._handle_input)
        self._input_queue = None

        # Asynchronous class variables
        self._loop = None
        self._manager_process = None
        self._running = asyncio.Event()

    def _handle_input(self, widget: ptg.InputField, key):
        """Handle input field key events.

        If the Enter key is pressed, retrieves the input value,
        clears the input field, and processes the command.
        This function doesn't actually manage the keypresses, but is
        called by pytermgui when the appropriate key is detected.

        Args:
            widget: The input field widget.
            key: The key event.
        Returns:
            bool: True, since the input was handled.
        """
        command = widget.value.strip()
        widget.delete_back(len(widget.value))

        if not self._loop or not self._input_queue:
            return True

        if self._input_queue.full():
            return True

        self._loop.call_soon_threadsafe(self._input_queue.put_nowait, command)
        return True

    async def run(self):
        """Start the UI manager and wait for shutdown signal.

        Initializes the UI manager in a background thread and waits for
        the shutdown event to be triggered. Once triggered, performs
        cleanup by stopping the manager and cancelling the background task.

        Note:
            This method blocks until stop() is called or a KeyboardInterrupt
            is received.
        """
        if self._manager_process:
            return

        self._loop = asyncio.get_running_loop()
        self._input_queue = asyncio.Queue(maxsize=1)

        self._manager.focus(self._input_window)
        self._input_field.select()
        self._manager_process = asyncio.create_task(asyncio.to_thread(self._manager.run))
        self._running.set()

    async def wait_until_running(self):
        """Wait until the UI manager is fully running.

        This method can be used to ensure that the UI is ready before
        performing operations that depend on the UI being active.
        """
        await self._running.wait()

    async def stop(self):
        """Signal the UI to shut down.

        Sets the shutdown event, which triggers the cleanup process in run().
        This method can be called from signal handlers or other contexts
        to gracefully terminate the UI.
        """
        if not self._manager_process:
            return

        self._running.clear()
        self._manager.stop()
        self._manager_process.cancel()
        try:
            await self._manager_process
        except asyncio.CancelledError:
            pass

        self._manager_process = None
        keyboard.press_and_release("enter")  # Wake up input field if waiting

    async def set_title(self, title: str, fmt: str = "#ffffff", window: str = "main"):
        """Set the title of the main window asynchronously.

        Args:
            title: The new title for the main window.
            fmt: The format string to apply to the title text.
                Defaults to white text.
        """
        def _set_title():
            match window:
                case "main":
                    self._main_window.set_title(f"[{fmt}]{title}[/]")
                case "hand":
                    self._hand_window.set_title(f"[{fmt}]{title}[/]")
                case _:
                    raise ValueError(f"Unknown window: {window}")

        await asyncio.to_thread(_set_title)

    async def input(self):
        """Asynchronously retrieve user input from the input field.

        Waits for the user to enter a command and press Enter, then
        returns the command as a string.

        Returns:
            str: The user-entered command.
        """
        if not self._input_queue:
            raise RuntimeError("UI is not running. Call run() before input().")

        command = await self._input_queue.get()
        return command

    async def println(self, *args: str, fmts: Optional[List[str]] = None, window: str = "main", sep: str = " ", end: str = "\n"):
        """Prints a line of text to a window asynchronously.
        Args:
            *args: The strings to print.
            fmts: Optional list of format strings for each argument.
                If not provided or empty, defaults to white text.
                If the number of formats is less than the number of arguments,
                the last format is applied to the remaining arguments.
            window: The window to print to ("main" or "hand").
                If not provided, defaults to "main".
            sep: The separator to use between arguments.
                If not provided, defaults to a single space.
            end: The string to append at the end of the line.
                If not provided, defaults to a newline.
        Raises:
            ValueError: If the number of formats exceeds the number of arguments
                or if an unknown window is specified.
        """

        # Default format is white text
        if fmts is None or len(fmts) == 0:
            fmts = ["#ffffff"] * len(args)

        # Extend formats to last applied format if not enough provided
        if len(fmts) < len(args):
            fmts += fmts[-1] * (len(args) - len(fmts))

        if len(fmts) > len(args):
            raise ValueError("Number of formats must be less than or equal to number of arguments")

        sstream = io.StringIO()

        # Write formatted arguments to string stream
        for fmt, arg in zip(fmts, args):
            print(f"[{fmt}]{str(arg)}[/]", end=sep, file=sstream)
        print(end, end="", file=sstream)

        # Prepare the label text
        label_text = sstream.getvalue().rstrip(sep)

        # Add widget to window in a thread-safe manner
        def _add_widget():
            match window:
                case "main":
                    self._main_text.value += label_text
                    self._main_window.scroll_end(-1)
                case "hand":
                    self._hand_text.value += label_text
                    self._hand_window.scroll_end(-1)
                case _:
                    raise ValueError(f"Unknown window: {window}")

        # Run the widget addition in a thread to avoid blocking
        await asyncio.to_thread(_add_widget)

    async def clear(self, window: str = "main"):
        """Clears all content from the specified window asynchronously.
        Args:
            window: The window to clear ("main" or "hand").
                If not provided, defaults to "main".
        Raises:
            ValueError: If an unknown window is specified.
        """

        def _clear_window():
            match window:
                case "main":
                    self._main_text.value = ""
                case "hand":
                    self._hand_text.value = ""
                case _:
                    raise ValueError(f"Unknown window: {window}")

        # Run the window clearing in a thread to avoid blocking
        await asyncio.to_thread(_clear_window)
        self._manager.compositor.redraw()


# ============================================================================
# MAIN GAME LOGIC
# ============================================================================

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

    await ui.clear()

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
    await ui.clear(window="hand")
    await ui.set_title("Game Over", fmt="210 bold")
    await ui.set_title("Game Over", fmt="210 bold", window="hand")

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
