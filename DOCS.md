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

### Class Hierarchy: The Card Family Tree

In Flip 7, we have different types of cards. To keep things organized, we arrange them in a hierarchy, much like a family tree. This allows different cards to share common traits without us having to write the same code over and over.

```
BaseCard (The Ancestor - all cards come from here)
├── AddableCard (Cards with numbers)
│   ├── NumberCard (0-12)
│   └── ScoreModifierCard (+2, +10, x2, etc.)
└── ActionCard (Special effect cards)
```

**Why organize cards this way?**

Imagine you're defining vehicles. A "Car" and a "Truck" are different, but they both share traits of a "Vehicle" (like having wheels and an engine).

- **BaseCard** is like "Vehicle" - it defines what it means to be a card.
- **AddableCard** is a specific category of cards that have numbers.
- **NumberCard** and **ScoreModifierCard** are specific types of AddableCards.
- **ActionCard** is a different branch for cards that *do* things rather than just having a value.

This structure (called **inheritance**) lets us say "A NumberCard is a type of AddableCard, which is a type of BaseCard."

## The Classes Explained

### Card Classes

#### `BaseCard`
The "concept" of a card. You can't actually hold a "BaseCard" in your hand—it's just a template that says "every card must be able to show itself as a text string." In programming terms, this is an **abstract class**.

#### `AddableCard`
A category for cards that have a number value. It builds on `BaseCard` by adding a `value` property. Both `NumberCard` and `ScoreModifierCard` belong to this category because they both contribute numbers to the game.

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
Cards that trigger special effects when drawn. These cards don't have values but perform specific actions. We have three specific types of action cards:

- **`FreezeCard`**: Immediately locks a targeted player out of the round and banks their current score.
- **`FlipThreeCard`**: Forces a targeted player to draw three more cards from the deck.
- **`SecondChanceCard`**: Gives the player a "second chance" token that protects them from busting once.

When a player draws an action card (except Second Chance), they get to choose which opponent to target!

### Game Management Classes

#### `Deck`
Manages the collection of all cards used in the game. The Deck class:
- Automatically creates and stores all the cards when initialized
- Contains the correct quantities of each card type:
  - Number cards: twelve 12s, eleven 11s, ten 10s, down to one 1, plus one 0
  - Score modifiers: one of each from +2 to +10, plus six x2 multipliers
  - Action cards: four of each type (Freeze, Flip Three, Second Chance)
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
- Knows who the other players are (to target them with action cards)
- Has callback functions for printing messages and getting input (connected to the UI)
- Can perform actions like:
  - **Hit:** Draw a card from the deck. If it's an action card, it might trigger immediately!
  - **Stay:** End their turn and lock in their score
  - **Take Action:** When drawing an action card, choose another player to target (requires user input!)
  - **Check for bust:** See if they drew duplicate NumberCards (accounting for second chances)
  - **Check for seven:** See if they collected seven unique NumberCards
  - **Get score:** Retrieve the player's current total score
  - **Update score:** Calculate points based on their cards (number cards + modifiers)
  - **Add bonus:** Award the 15-point bonus for collecting seven unique cards
  - **Reset:** Clear the hand and prepare for a new round
  - **Manage second chances:** Track and use second chance tokens to avoid busting
  - **Receive card:** Add a card directly to the hand (used by FlipThreeCard)
  - **Check for game win:** See if their total score has reached 200

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

# Let players know about each other (for action card targeting)
player1.set_players([player1, player2])
player2.set_players([player1, player2])

# Shuffle the deck
deck.shuffle()

# Player 1 draws a card
await player1.hit(deck)

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

You might notice some funny-looking methods with double underscores, like `__init__` or `__str__`. These are **Special Methods** (often called "dunder" methods for **d**ouble **under**score).

Think of them as the "magic words" that let your custom objects behave like built-in Python things.

For example:
- `__str__` tells Python how to print your object nicely.
- `__eq__` tells Python how to check if two objects are equal (`==`).
- `__len__` tells Python what to do when you ask for the `len()` of your object.

Without these, your objects would feel clunky. With them, they feel like a natural part of the language!

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

## Understanding Asynchronous Code: Making the UI Responsive

If you look at the `UI` class in `ui.py`, you'll notice some unusual keywords like `async` and `await`. This is **asynchronous programming**, and while it might seem intimidating at first, the concept is actually quite intuitive!

### The Problem: Waiting Around

Imagine you're cooking dinner and you need to:
1. Boil water (takes 10 minutes)
2. Chop vegetables (takes 5 minutes)
3. Cook pasta (takes 8 minutes)

If you did these tasks **synchronously** (one after another), you'd:
- Start boiling water → wait 10 minutes doing nothing
- Then chop vegetables → 5 minutes
- Then cook pasta → 8 minutes
- Total time: 23 minutes

But that's inefficient! While the water is boiling, you could be chopping vegetables. This is what **asynchronous** programming is all about - doing other work while waiting for something to finish.

### How Async Works in Our Game

In our Flip 7 game, the UI needs to:
- Display game information on the screen
- Wait for the user to type commands
- Update the display when cards are drawn
- Handle multiple things happening at once

Without async, the game would freeze while waiting for user input - you couldn't see updates or animations. With async, the UI can stay responsive!

### Key Async Concepts

#### `async` Functions

When you see `async def` instead of just `def`, it means "this function might need to wait for something, but it won't block everything else."

```python
async def input(self):
    """Wait for user to type something"""
    command = await self._input_queue.get()
    return command
```

The `async` keyword says: "This function involves waiting, so let other code run while we wait."

#### `await` Keyword

The `await` keyword means "wait for this to finish, but let other async tasks run in the meantime."

```python
command = await ui.input()  # Wait for user input, but UI stays responsive
print(f"You typed: {command}")  # Only runs after user presses Enter
```

Think of `await` like saying "I'll wait here, but others can keep working."

#### Why Our UI Uses Async

Look at the `UI` class methods:

**`async def run(self)`**: Starts the UI manager in the background. It uses `await asyncio.to_thread()` to run the UI in a separate thread, so it doesn't block the game logic.

**`async def input(self)`**: Waits for user input without freezing the entire program. While waiting for the user to type, the UI can still update the display, show animations, or handle other events.

**`async def println(self, *args, ...)`**: Prints to the screen without blocking. Even though printing is usually fast, doing it asynchronously ensures the UI never freezes, even if it gets many print requests at once.

**`async def stop(self)`**: Gracefully shuts down the UI by cancelling the background task and cleaning up resources.

### Real-World Example from Our Game

Here's what happens when a player draws a card:

```python
# Player draws a card (async because it needs to print to UI)
card = await player.hit(deck)

# The hit() method prints the card drawn
await self._print(f"Player {self._id} drew {card}")

# If it's an action card, we need user input
if isinstance(card, ActionCard):
    await self._print("Choose a target player:")
    target_id = await self._input()  # Wait for user to type
    # ... rest of the logic
```

Notice how everything that interacts with the UI (printing or getting input) uses `await`. This ensures:
1. The UI updates immediately when cards are drawn
2. The game waits properly for user input
3. The display never freezes or becomes unresponsive
4. Multiple players could potentially interact simultaneously (in a networked version)

### The Event Loop: The Conductor

Behind the scenes, Python's `asyncio` library uses an **event loop** - think of it as a conductor coordinating an orchestra. It manages all the async tasks, deciding which one should run at any given moment.

When you run an async program, you start it with:
```python
asyncio.run(main())
```

This creates an event loop that:
1. Starts your `main()` function
2. Whenever it hits an `await`, it pauses that task and runs other tasks
3. When an awaited operation finishes (like user input arriving), it resumes that task
4. Keeps juggling tasks until everything is done

### Why Not Just Use Threads?

You might think, "Can't we just use multiple threads?" We could, but:
- Threads are heavier and use more memory
- Threads can have race conditions (two threads modifying the same data)
- Async is perfect for I/O-bound tasks (waiting for input, network, file reads)
- Async code is often easier to reason about than multi-threaded code

Our UI actually uses *both* - it runs the pytermgui manager in a thread (`asyncio.to_thread()`), but coordinates with it using async/await!

### Don't Worry If It's Confusing!

Async programming is an advanced topic. For this class, the key takeaways are:
1. `async def` creates a function that can pause and resume
2. `await` means "wait for this, but let other things run"
3. It makes our UI responsive and smooth
4. You need `await` when calling any `async` function

You don't need to master async programming to understand the game logic - just know that it's what keeps the UI from freezing while waiting for your input!

### Further Reading

If you're curious to learn more about async programming:
- Python's official `asyncio` documentation
- "Async/await" tutorials for Python
- Search for "Python concurrency" to understand different approaches

But for now, focus on understanding classes, objects, and game logic - async is just the "magic" that makes the UI work smoothly!

