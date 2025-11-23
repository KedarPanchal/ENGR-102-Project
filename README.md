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
- Automatically creates and stores all the cards when initialized
- Contains the correct quantities of each card type:
  - Number cards: twelve 12s, eleven 11s, ten 10s, down to one 1, plus one 0
  - Score modifiers: one of each from +2 to +10, plus one x2 multiplier
  - Action cards: (to be added when implemented)
- Can shuffle the cards randomly
- Allows players to draw cards from the top
- Can accept returned cards (when rounds end and cards are discarded)

Think of it like the actual deck of cards sitting on the table that everyone draws from. When you create a Deck object, it automatically fills itself with all the cards needed for the game!

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

1. A **Deck** object is created, which automatically fills itself with all the card objects (NumberCards, ScoreModifierCards, and ActionCards)
2. **Player** objects are created for each person playing
3. The deck shuffles its cards using the `shuffle()` method
4. Each player takes turns calling their `hit()` method to draw cards from the deck
5. Players check if they're busted or have won with `is_busted()` and `has_seven()`
6. When a player decides to stay, they call `stay()` which calculates their final score
7. After the round, cards are returned to the deck with `return_cards()`
8. The game continues until someone's score reaches 200 or higher!

**Example in code:**
```python
# Create a deck (it automatically fills itself with cards)
deck = Deck()

# Create players
player1 = Player(1)
player2 = Player(2)

# Shuffle the deck
deck.shuffle()

# Player 1 draws a card
player1.hit(deck)

# Check if player 1 has seven unique cards
if player1.has_seven():
    print("Player 1 wins the round!")
```

## Why Use Classes?

You might wonder: why not just use simple variables and functions?

Classes help us:
- **Organize related data together:** A Player's ID, score, hand, and active status all belong together
- **Avoid confusion:** Instead of having variables like `player1_score`, `player2_score`, etc., each Player object manages its own score
- **Reuse code:** We can create as many Player objects as needed without rewriting code
- **Model the real world:** The game has cards, players, and a deck in real life, and our code reflects that!

This is the essence of **Object-Oriented Programming (OOP)** - organizing code around "objects" that represent things in your program, making it easier to understand, maintain, and expand.

## Special Methods: Making Objects Work Like Built-in Types

You may have noticed some methods in our classes with double underscores on each side, like `__init__`, `__str__`, or `__eq__`. These are called **special methods** (or "dunder methods" - short for "double underscore"). They're Python's way of letting us customize how our objects behave in certain situations.

Think of special methods like teaching your custom objects to speak Python's language. They allow you to:
- Print your objects in a readable way
- Compare them to each other
- Loop through them
- Get their length
- And much more!

Let's look at the special methods we use in our Flip 7 game:

### String Representation: `__str__`

**What they do:** Control how objects are displayed when printed or converted to strings.

**Why we need them:** Without these methods, printing a card would show something unhelpful like `<card.NumberCard object at 0x7f8b1c2d3e80>`. With them, we can make it show `7` or `+10` instead!

**Where we use them:**

- **`BaseCard.__str__`**: Every card type must define how it looks as a string
- **`NumberCard`**: Inherited from `AddableCard`, shows just the number (e.g., `"7"`)
- **`ScoreModifierCard.__str__`**: Shows the modifier type and value (e.g., `"+10"` or `"x2"`)
- **`Player.__str__`**: Shows the player's ID, score, and hand in a readable format
- **`Deck.__str__`**: Lists all cards in the deck separated by spaces

**Example:**
```python
card = NumberCard(7)
print(card)  # Output: 7

modifier = ScoreModifierCard(10, True)
print(modifier)  # Output: +10

player = Player(1)
player.hand.append(NumberCard(5))
print(player)  # Output: Player 1 Score: 0\nHand: 5
```

### Equality Comparison: `__eq__`

**What it does:** Defines how to check if two objects are "equal" using the `==` operator.

**Why we need it:** We need to detect when a player draws duplicate NumberCards (which causes a bust). Without `__eq__`, Python would only check if two cards are the exact same object in memory, not if they have the same value.

**Where we use it:**

- **`NumberCard.__eq__`**: Two NumberCards are equal if they have the same value

**Example:**
```python
card1 = NumberCard(7)
card2 = NumberCard(7)
card3 = NumberCard(8)

print(card1 == card2)  # Output: True (same value)
print(card1 == card3)  # Output: False (different values)

# This is how we detect duplicates!
if card1 == card2:
    print("Bust! You drew a duplicate!")
```

### Hashing: `__hash__`

**What it does:** Creates a unique identifier (hash) for an object so it can be stored in sets or used as dictionary keys.

**Why we need it:** Sets automatically remove duplicates, which is perfect for checking if a player has seven **unique** NumberCards. But Python can only put objects in sets if they can be hashed.

**Where we use it:**

- **`NumberCard.__hash__`**: Creates a hash based on the card's value

> [!NOTE]
> You won't directly call `__hash__` in your game code. Instead, it's used internally by Python when you work with sets or dictionaries. When you write `set(hand)` or check `if card in some_set`, Python automatically calls `__hash__` behind the scenes. The `Player` class uses this indirectly in methods like `has_seven()` and `is_busted()` which convert card lists to sets.

**Example:**
```python
hand = [NumberCard(3), NumberCard(7), NumberCard(3), NumberCard(9)]

# Convert to a set - duplicates automatically removed!
# Python calls __hash__ on each card internally
unique_cards = set(hand)
print(len(unique_cards))  # Output: 3 (only 3, 7, and 9)

# This is how we check for seven unique cards!
if len(unique_cards) == 7:
    print("You win the round!")
```

### Iteration: `__iter__`

**What it does:** Makes an object "iterable," meaning you can loop through it with a `for` loop.

**Why we need it:** Players need to loop through their hand to check cards, and we might want to loop through all cards in the deck.

**Where we use it:**

- **`Player.__iter__`**: Allows looping through a player's hand
- **`Deck.__iter__`**: Allows looping through all cards in the deck

**Example:**
```python
player = Player(1)
player.hand = [NumberCard(5), NumberCard(7), ScoreModifierCard(10, True)]

# We can loop through the player's hand directly!
for card in player:
    print(card)  # Output: 5, then 7, then +10

# This is equivalent to:
for card in player.hand:
    print(card)
```

### Length: `__len__`

**What it does:** Defines what `len(object)` returns for your custom object.

**Why we need it:** It's more intuitive to check `len(deck)` than `len(deck._cards)`.

**Where we use it:**

- **`Deck.__len__`**: Returns the number of cards in the deck

**Example:**
```python
deck = Deck()
print(len(deck))  # Output: 87 (total number of cards initially)

deck.take_card()
print(len(deck))  # Output: 86 (one card removed)
```

### Why These Special Methods Matter

These special methods make our custom objects (cards, players, decks) behave like Python's built-in types (lists, numbers, strings). This means:

1. **More intuitive code**: `print(card)` instead of `print(card.get_string_representation())`
2. **Built-in Python features work**: You can use `card1 == card2`, `for card in player`, `len(deck)`
3. **Cleaner logic**: Checking for duplicates is as simple as `set(hand)` instead of writing complex loops
4. **Professional coding style**: Your code looks and feels like standard Python

These special methods are part of what makes Python such a powerful and expressive language - you can create your own types that work seamlessly with all of Python's features!

