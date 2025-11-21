from .card import *
from .deck import Deck
from typing import List

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
        self.score = 0
        self.hand: List[BaseCard] = []

    def hit(self, deck: Deck) -> bool:
        """Draw a card from the deck and add it to the player's hand.
        
        Args:
            deck: The deck to draw a card from.
            
        Returns:
            The class type of the drawn card if successful, False otherwise.
        """
        card = deck.take_card()
        if card:
            self.hand.append(card)
            return card.__class__
        return False
    
    def stay(self) -> bool:
        """Check if the player's hand consists only of score modifier cards.
        
        Returns:
            True if all cards in hand are ScoreModifierCards, False otherwise.
        """
        for card in self.hand:
            if not isinstance(card, ScoreModifierCard):
                return False
        return True
    
    def is_busted(self) -> bool:
        """Check if the player has duplicate number cards (bust condition).
        
        Returns:
            True if the player has duplicate NumberCards, False otherwise.
        """
        number_cards = filter(lambda card: isinstance(card, NumberCard), self.hand)
        return len(number_cards) != len((set(number_cards)))
    
    def has_seven(self) -> bool:
        """Check if the player has exactly seven unique number cards.
        
        Returns:
            True if the player has seven unique NumberCards, False otherwise.
        """
        return len(set(filter(lambda card: isinstance(card, NumberCard), self.hand))) == 7
    
    def add_points(self, points: int):
        """Add points to the player's score.
        
        Args:
            points: Number of points to add to the player's score.
        """
        self.score += points

    def __iter__(self):
        """Allow iteration over the player's hand of cards.
        
        Returns:
            Iterator over the cards in the player's hand.
        """
        return iter(self.hand)