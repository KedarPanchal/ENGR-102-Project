```mermaid
---
title: Class Diagram
---
classDiagram
    class BaseCard {
        +__str__(self) str
    }

    class AddableCard {
        -_value: int
        +__init__(self, value) None
        +value(self) int
        +__str__(self) str
    }
    BaseCard <|-- AddableCard

    class NumberCard {
        ~__hash__(self) int
        +__eq__(self, other) bool
    }
    AddableCard <|-- NumberCard

    class ScoreModifierCard {
        -_is_addition: bool
        +__init__(self, modifier, is_addition) None
        +is_addition(self) bool
        +__str__(self) str
    }
    AddableCard <|-- ScoreModifierCard

    class ActionCard {
        +action(self, targeted_player) None
    }
    BaseCard <|-- ActionCard

    class FreezeCard {
        +__str__(self) str
    }
    ActionCard <|-- FreezeCard

    class SecondChanceCard {
        +__str__(self) str
    }
    ActionCard <|-- SecondChanceCard

    class FlipThreeCard {
        -_deck Deck
        +__init__(self, deck) None
        +__str__(self) str
    }
    ActionCard <|-- FlipThreeCard
    FlipThreeCard ..> Deck: "Takes cards from"


    class Deck {
        -_cards: List[BaseCard]
        +__init__(self) None
        +shuffle(self) None
        +take_card(self) BaseCard | None
        +return_cards(self, cards) None
        +__iter__(self) Iterator[BaseCard]
        +__len__(self) int
        +__str__(self) str
    }
    BaseCard ..> Deck: "Managed by" 


    class Player {
        -_id: int
        -_score: int
        -_hand: List[BaseCard]
        -_active: bool
        -_opponents: List[Player]
        -_second_chance: bool
        +__init__(self, id) None
        +set_opponents(self, opponents) None
        +is_active(self) bool
        +hit(self, deck) None
        +stay(self) None
        +is_busted(self) bool
        +has_seven(self) bool
        +add_bonus(self) None
        +update_score(self) None
        +reset(self) List[BaseCard]
        ~take_action(self, card) None
        ~has_second_chance(self) bool
        ~add_second_chance(self) None
        ~use_second_chance(self) None
        ~receive_card(self, card) None
        +won_game(self) bool
        +__iter__(self) Iterator[BaseCard]
        +__str__(self) str
    } 
    Deck ..> Player: "Gives cards to on hit" 
    Player ..> Deck: "Returns cards on reset to" 
    BaseCard ..> Player: "Held by" 
    ActionCard ..> Player: "Targets" 
    Player ..> AddableCard: "Calculates score using"
```
