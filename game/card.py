from abc import ABC, abstractmethod

class BaseCard(ABC):
    """Abstract base class for all card types in the Flip Seven game.
    
    This class serves as the foundation for all card implementations,
    ensuring a consistent interface across different card types.
    """
    pass

class NumberCard(BaseCard):
    """Represents a numbered card in the Flip Seven game.
    
    Number cards have a numeric value and can be compared for equality.
    Players collect sets of unique number cards to achieve victory.
    
    Attributes:
        _value: The numeric value of the card.
    """
    
    def __init__(self, value: int):
        """Initialize a NumberCard with a specific value.
        
        Args:
            value: The numeric value for this card.
        """
        self._value = value

    def value(self):
        """Get the numeric value of the card.
        
        Returns:
            The card's numeric value.
        """
        return self._value
    
    def __hash__(self):
        """Compute hash based on the card's value.
        
        Returns:
            Hash value of the card.
        """
        return hash(self._value)
    
    def __eq__(self, other):
        """Check equality with another card.
        
        Args:
            other: Another object to compare with.
            
        Returns:
            True if both are NumberCards with the same value, False otherwise.
        """
        if isinstance(other, NumberCard):
            return self._value == other._value
        return False


class ScoreModifierCard(BaseCard):
    """Represents a card that modifies player scores.
    
    These cards affect the scoring mechanism of the game when played.
    """
    pass


class ActionCard(BaseCard):
    """Represents a card that triggers special actions.
    
    Action cards provide special game effects when played.
    """
    pass