from .card import (
    AddableCard,
    BaseCard,
    NumberCard,
    ScoreModifierCard,
    ActionCard
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

    def hit(self, deck: Deck) -> bool:
        """Draw a card from the deck and add it to the player's hand.

        If the drawn card is an ActionCard, its action is immediately executed.
        The player must be active to draw cards.

        Args:
            deck: The deck to draw a card from.

        Returns:
            True if a card was successfully drawn, False otherwise.
        """
        if not self._active:
            return False

        card = deck.take_card()
        if not card:
            return False

        self._hand.append(card)
        if isinstance(card, ActionCard):
            # TODO: Make the target player an actual targeted player
            card.action(self)

        return True

    def stay(self) -> None:
        """End the player's turn and finalize their score for the round.

        Marks the player as inactive and calculates their final score
        based on the cards in their hand.
        """
        self._active = False
        self.update_score()

    def is_busted(self) -> bool:
        """Check if the player has duplicate number cards (bust condition).

        Returns:
            True if the player has duplicate NumberCards, False otherwise.
        """
        number_cards = [card for card in self._hand if isinstance(card, NumberCard)]
        return len(number_cards) != len((set(number_cards)))

    def has_seven(self) -> bool:
        """Check if the player has exactly seven unique number cards.

        Returns:
            True if the player has seven unique NumberCards, False otherwise.
        """
        return len({card for card in self._hand if isinstance(card, NumberCard)}) == 7

    def add_bonus(self) -> None:
        """Add a bonus to the player's score if they have seven unique cards.

        Awards 15 bonus points if the player has exactly seven unique number
        cards without duplicates.
        """
        if self.has_seven() and not self.is_busted():
            self._score += 15

    def update_score(self) -> None:
        """Calculate and update the player's score based on cards in hand.

        Applies all score modifiers (multipliers first, then additions) and
        adds the values of all number cards to calculate the final score.
        """
        total_multiplier = 1
        total_addition = 0
        for card in self._hand:
            if not isinstance(card, AddableCard):
                continue
            if isinstance(card, ScoreModifierCard):
                if card.is_addition():
                    total_addition += card.value()
                else:
                    total_multiplier *= card.value()
            elif isinstance(card, NumberCard):
                total_addition += card.value()

        self._score *= total_multiplier
        self._score += total_addition

    def reset(self) -> List[BaseCard]:
        """Reset the player's state for a new round.

        Returns:
            The list of cards that were in the player's hand.
        """
        self._active = True
        discarded_hand = self._hand[:]
        self._hand = []
        return discarded_hand

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
