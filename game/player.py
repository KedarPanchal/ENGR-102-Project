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
        score: Current score of the player.
        hand: List of cards currently held by the player.
    """

    def __init__(self, id: int):
        """Initialize a new player.

        Args:
            id: Unique identifier for this player.
        """
        self.id = id
        self._score = 0
        self.hand: List[BaseCard] = []
        self.active = True

    def hit(self, deck: Deck) -> bool:
        """Draw a card from the deck and add it to the player's hand.

        Args:
            deck: The deck to draw a card from.

        Returns:
            True if the card was able to be drawn, False otherwise.
        """
        if not self.active:
            return False

        card = deck.take_card()
        if not card:
            return False

        self.hand.append(card)
        if isinstance(card, ActionCard):
            # TODO: Make the target player an actual targeted player
            card.action(self)

        return True

    def stay(self) -> None:
        """Check if the player's hand consists only of score modifier cards.

        Returns:
            True if all cards in hand are ScoreModifierCards, False otherwise.
        """
        self.active = False
        self.update_score()

    def is_busted(self) -> bool:
        """Check if the player has duplicate number cards (bust condition).

        Returns:
            True if the player has duplicate NumberCards, False otherwise.
        """
        number_cards = [card for card in self.hand if isinstance(card, NumberCard)]
        return len(number_cards) != len((set(number_cards)))

    def has_seven(self) -> bool:
        """Check if the player has exactly seven unique number cards.

        Returns:
            True if the player has seven unique NumberCards, False otherwise.
        """
        return len({card for card in self.hand if isinstance(card, NumberCard)}) == 7

    def add_bonus(self):
        if self.has_seven() and not self.is_busted():
            self._score += 15

    def update_score(self):
        total_multiplier = 1
        total_addition = 0
        for card in self.hand:
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
        self.active = True
        discarded_hand = self.hand[:]
        self.hand = []
        return discarded_hand

    def won_game(self) -> bool:
        return self._score >= 200

    def __iter__(self) -> Iterator[BaseCard]:
        """Allow iteration over the player's hand of cards.

        Returns:
            Iterator over the cards in the player's hand.
        """
        return iter(self.hand)
