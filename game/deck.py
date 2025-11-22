from .card import BaseCard, NumberCard, ScoreModifierCard
from typing import List
import random


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
        self.cards: List[BaseCard] = []
        for number in range(1, 13):
            for _ in range(number):
                self.cards.append(NumberCard(number))
        self.cards.append(NumberCard(0))

        for i in range(2, 11):
            self.cards.append(ScoreModifierCard(i, True))
        self.cards.append(ScoreModifierCard(2, False))

        # TODO: Add ActionCards when their implementation is complete

    def shuffle(self):
        """Randomly shuffle the cards in the deck."""
        random.shuffle(self.cards)

    def take_card(self):
        """Draw a card from the top of the deck.

        Returns:
            The top card from the deck, or None if the deck is empty.
        """
        return self.cards.pop() if self.cards else None

    def return_cards(self, cards: List[BaseCard]):
        """Return a list of cards back to the deck.

        Args:
            cards: List of cards to return to the deck.
        """
        self.cards += cards
