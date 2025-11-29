from .card import (
    AddableCard,
    BaseCard,
    NumberCard,
    ScoreModifierCard,
    ActionCard,
    SecondChanceCard
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
        self._opponents = []
        self._second_chance = False

    def set_opponents(self, opponents) -> None:
        """Set the list of opponent players.

        Args:
            opponents: List of other Player instances in the game.
        """

        for opponent in opponents:
            if opponent._id != self._id:
                self._opponents.append(opponent)

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
            if isinstance(card, SecondChanceCard):
                card.action(self)
            else:
                self.take_action(card)

        return True

    def take_action(self, action_card: ActionCard) -> None:
        """Execute the action of an ActionCard on this player.

        Args:
            action_card: The ActionCard to be executed.
        """
        targeted_player = None
        while True:
            targeted_id = input("Select a player ID to target with the action card: ")
            if not targeted_id.isdigit():
                print("Invalid input. Please enter a numeric player ID.")
                continue

            targeted_id = int(targeted_id)
            matching_ids = [opponent._id for opponent in self._opponents if opponent._id == targeted_id]
            # None or multiple matches
            if len(matching_ids) != 1:
                print("No matching player found. Please try again.")

            targeted_player = matching_ids[0]
            break

        if targeted_player:
            action_card.action(targeted_player)

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
        return not self._second_chance and (len(number_cards) != len((set(number_cards))))

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
