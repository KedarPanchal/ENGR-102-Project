from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .player import Player
    from .deck import Deck


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
    def action(self, targeted_player: 'Player') -> None:
        """Perform the action associated with this card.

        Args:
            targeted_player: The player affected by the action.
        """
        pass


class FreezeCard(ActionCard):
    """Represents a Freeze action card that skips a player's next turn."""

    def action(self, targeted_player: Player) -> None:
        """Skip the targeted player's next turn.

        Args:
            targeted_player: The player to be frozen.
        """
        targeted_player.stay()

    def __str__(self) -> str:
        """Provide a string representation of the Freeze card.

        Returns:
            A string indicating this is a Freeze card.
        """
        return "Freeze!"


class SecondChanceCard(ActionCard):
    """Represents a Second Chance action card that allows a player to draw again."""

    def action(self, targeted_player: Player) -> None:
        """Allow the targeted player to draw another card.

        Args:
            targeted_player: The player who gets a second chance.
        """
        targeted_player.add_second_chance()

    def __str__(self) -> str:
        """Provide a string representation of the Second Chance card.

        Returns:
            A string indicating this is a Second Chance card.
        """
        return "Second Chance!"


class FlipThreeCard(ActionCard):
    def __init__(self, deck: Deck) -> None:
        """Initialize a Flip Three action card with a reference to the deck."""
        self._deck = deck

    def action(self, targeted_player: Player) -> None:
        """Force the targeted player to flip three cards.

        Args:
            targeted_player: The player who must flip three cards.
        """
        action_card_stack = []
        for _ in range(3):
            card = self._deck.take_card()
            if not card:
                break
            if isinstance(card, ActionCard):
                action_card_stack.append(card)
            else:
                targeted_player.receive_card(card)
                if targeted_player.is_busted() or targeted_player.has_seven():
                    break
        while action_card_stack:
            action_card = action_card_stack.pop()
            targeted_player.take_action(action_card)

    def __str__(self) -> str:
        """Provide a string representation of the Flip Three card.

        Returns:
            A string indicating this is a Flip Three card.
        """
        return "Flip Three!"
