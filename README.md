# ENGR 102 - Flip 7 Game

## What is Flip 7?

Flip 7 is a press-your-luck card game where players compete to reach 200 total points. Each round, players draw cards trying to collect exactly seven unique number cards without getting duplicates (which causes a "bust"). The game includes number cards, score modifier cards, and action cards that add strategy and excitement.

## Understanding Classes: Building Blocks of the Game

Think of **classes** like blueprints or templates. Just like an architect creates a blueprint for a house that can be used to build many actual houses, we create classes in programming to define what something should be and what it can do.

In our Flip 7 game, we use classes to represent the different "things" in the game: cards, players, and the deck. Each class is like a recipe that tells Python:
- What **properties** (data) that thing should have
- What **actions** (functions) that thing can do

For example, every Player in the game needs:
- An ID number to identify them
- A score to track their points
- A hand to hold their cards
- The ability to draw cards, stay, or check if they've won

The class is the blueprint, and when we actually create a player in our game (like "Player 1" or "Player 2"), we call that an **instance** or **object** of the class.

## Class Hierarchy: How Cards Are Organized

In Flip 7, we have different types of cards, and they're organized in a hierarchy (like a family tree). This helps us organize our code and avoid repeating ourselves.

```
BaseCard (the "grandparent" - all cards start here)
├── AddableCard (cards that have numeric values)
│   ├── NumberCard (cards numbered 0-12)
│   └── ScoreModifierCard (cards that add or multiply your score)
└── ActionCard (cards that trigger special effects)
```

**Why organize cards this way?**

Imagine if you had to write separate code for every single card type without any shared structure. You'd write the same code over and over! Instead, we use **inheritance** - a fancy word that means "child classes inherit traits from parent classes."

- **BaseCard** is the foundation - it says "this is a card in our game"
- **AddableCard** inherits from BaseCard and adds the concept of having a numeric value
- **NumberCard** and **ScoreModifierCard** both inherit from AddableCard because they both have values that affect scoring
- **ActionCard** inherits directly from BaseCard because it doesn't have a value - it just does something special

## The Classes Explained

### Card Classes

#### `BaseCard`
The foundation of all cards in the game. This is an abstract class, meaning you never create a BaseCard directly - it just defines that something "is a card." Think of it as saying "all cards in this game must follow certain rules."

#### `AddableCard`
A special type of card that has a numeric value. This class inherits from BaseCard and adds the ability to store and retrieve a number. Both NumberCards and ScoreModifierCards need numeric values, so they both build upon this class.

#### `NumberCard`
The main cards in the game, numbered from 0 to 12. These are the cards you collect to try to get seven unique ones. The deck contains different quantities of each number (twelve 12s, eleven 11s, down to one 1, and one 0). These cards:
- Have a value that adds to your score
- Can be compared to check for duplicates (which cause a bust)
- Count toward the goal of collecting seven unique cards

**Example:** If you draw a 7 card, it's a NumberCard with a value of 7.

#### `ScoreModifierCard`
Special cards that change how your score is calculated. These cards:
- Can add to your score (like +2 or +10)
- Can multiply your score (like x2, which doubles your number card total)
- Don't count toward the seven unique cards you need
- Are applied after number cards when calculating your final score

**Example:** If you have number cards totaling 20 points and draw a +10 modifier, you'd score 30 points.

#### `ActionCard`
Cards that trigger special effects when drawn, targeting any active player. These cards don't have values but perform actions like:
- **Freeze:** Immediately locks a player out and banks their current score
- **Flip Three:** Forces a player to draw three more cards
- **Second Chance:** Protects against one duplicate (saves you from busting once)

### Game Management Classes

#### `Deck`
Manages the collection of all cards used in the game. The Deck class:
- Stores all the cards in a list
- Can shuffle the cards randomly
- Allows players to draw cards from the top
- Can accept returned cards (when rounds end and cards are discarded)

Think of it like the actual deck of cards sitting on the table that everyone draws from.

#### `Player`
Represents each person playing the game. The Player class:
- Tracks the player's ID (like Player 1, Player 2, etc.)
- Maintains their current score (stored privately as `_score`)
- Holds their hand of cards
- Knows if they're still active in the current round
- Can perform actions like:
  - **Hit:** Draw a card from the deck
  - **Stay:** End their turn and lock in their score
  - **Check for bust:** See if they drew duplicate NumberCards
  - **Check for seven:** See if they collected seven unique NumberCards
  - **Calculate score:** Determine points based on their cards

The Player class also handles the special rule that drawing seven unique NumberCards awards a 15-point bonus!

## How It All Works Together

When you play Flip 7:

1. A **Deck** object is created and filled with all the card objects (NumberCards, ScoreModifierCards, and ActionCards)
2. **Player** objects are created for each person playing
3. The deck shuffles its cards
4. Each player takes turns calling their `hit()` method to draw cards from the deck
5. Players check if they're busted or have won with `is_busted()` and `has_seven()`
6. When a player decides to stay, they call `stay()` which calculates their final score
7. After the round, cards are returned to the deck with `return_cards()`
8. The game continues until someone's score reaches 200 or higher!

## Why Use Classes?

You might wonder: why not just use simple variables and functions?

Classes help us:
- **Organize related data together:** A Player's ID, score, hand, and active status all belong together
- **Avoid confusion:** Instead of having variables like `player1_score`, `player2_score`, etc., each Player object manages its own score
- **Reuse code:** We can create as many Player objects as needed without rewriting code
- **Model the real world:** The game has cards, players, and a deck in real life, and our code reflects that!

This is the essence of **Object-Oriented Programming (OOP)** - organizing code around "objects" that represent things in your program, making it easier to understand, maintain, and expand.

