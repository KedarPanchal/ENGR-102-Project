from .card import (
    AddableCard,
    BaseCard,
    NumberCard,
    ScoreModifierCard,
    ActionCard,
)
from .deck import Deck
from typing import List, Iterator


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
