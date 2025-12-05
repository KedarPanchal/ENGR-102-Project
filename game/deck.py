from .card import (
        BaseCard,
        NumberCard,
        ScoreModifierCard,
        FreezeCard,
        SecondChanceCard,
        FlipThreeCard
)
from typing import List, Iterator
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
        self._cards: List[BaseCard] = []
        # # Add NumberCards
        # for number in range(1, 13):
        #     for _ in range(number):
        #         self._cards.append(NumberCard(number))
        # self._cards.append(NumberCard(0))
        # # Add ScoreModifierCards
        # for i in range(2, 11):
        #     self._cards.append(ScoreModifierCard(i, True))
        # self._cards.append(ScoreModifierCard(2, False))
        # # Add ActionCards
        # self._cards.append(FreezeCard())
        # self._cards.append(SecondChanceCard())
        # self._cards.append(FlipThreeCard(self))
        for number in range(0, 13):
            self._cards.append(NumberCard(number))
        # Add ActionCards
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
