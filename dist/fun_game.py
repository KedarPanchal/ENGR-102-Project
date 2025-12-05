# By submitting this assignment, I agree to the following:
# "Aggies do not lie, cheat, or steal, or tolerate those who do."
# "I have not given or received any unauthorized aid on this assignment."
#
# Names: Kedar Panchal
# Blane Weiblen
# Nate Waguespack
# Joshua Le
# Section: 213
# Assignment: Lab 13
# Date: 5 December 2025
#
#

"""
Flip 7 Game - Consolidated Version
All game logic, UI, and main code in a single file.
"""

import asyncio
import io
import keyboard
import pytermgui as ptg
import random
from abc import ABC, abstractmethod
from typing import List, Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


# ============================================================================
# CARD CLASSES
# ============================================================================

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