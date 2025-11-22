from abc import ABC, abstractmethod


class BaseCard(ABC):
    """Abstract base class for all card types in the Flip Seven game.

    This class serves as the foundation for all card implementations,
    ensuring a consistent interface across different card types.
    """
    pass


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

    def value(self):
        """Get the numeric value of the card.

        Returns:
            The card's numeric value.
        """
        return self._value


class NumberCard(AddableCard):
    """Represents a numbered card in the Flip Seven game.

    Number cards have a numeric value and can be compared for equality.
    Players collect sets of unique number cards to achieve victory.
    Players must collect exactly seven unique number cards without duplicates.
    """

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

    def is_addition(self):
        """Check if the card is an addition modifier.

        Returns:
            True if the card adds to the score, False if it multiplies.
        """
        return self._is_addition


class ActionCard(BaseCard):
    """Represents a card that triggers special actions when drawn.

    Action cards provide special game effects that target players.
    Subclasses must implement the action method to define behavior.
    """

    @abstractmethod
    def action(self, targeted_player):
        """Perform the action associated with this card.

        Args:
            targeted_player: The player affected by the action.
        """
        pass

