from .card import BaseCard
from typing import List
import random


class Deck:
    """Manages a collection of cards for the Flip Seven game.
    
    The deck holds cards that can be shuffled and drawn by players.
    
    Attributes:
        cards: List of cards in the deck.
    """
    
    def __init__(self):
        """Initialize an empty deck."""
        self.cards: List[BaseCard] = []

    def shuffle(self):
        """Randomly shuffle the cards in the deck."""
        random.shuffle(self.cards)

    def take_card(self):
        """Draw a card from the top of the deck.
        
        Returns:
            The top card from the deck, or None if the deck is empty.
        """
        return self.cards.pop() if self.cards else None
