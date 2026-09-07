import random as rd
import os
from time import sleep

suits = ["♤", "♧", "♡", "◇"]
cards = []
game = True
play = True

# Add more bot names here as the roster grows.
BOT_NAMES = ["X0R", "Connor", "Zeee"]

# Used when the available bot-name list runs out.
NAME_SUFFIXES = [
    "'s son",
    "'s daughter",
    "'s mother",
    "'s father",
    "'s dog",
    "'s cat",
    "'s evil twin",
    "'s lawyer",
    "'s accountant",
    "'s tax collector",
]


# Player
class Player:
    def __init__(self, name: str):
        self.name: str = name
        self.hand: list = []
        self.score: int = 0
        self.busted: bool = True
        self.health: int = 100
        self.target: int = rd.randint(16, 21)
        self.hits_this_round: int = 0

    def clear_hand(self):
        """Empties the player's hand by clearing the list."""
        self.hand.clear()


# Setting deck
def new_deck():
    cards.clear()

    for suit in suits:
        cards.append(f"A{suit}")

        for i in range(2, 11):
            cards.append(str(i) + suit)

        cards.append(f"J{suit}")
        cards.append(f"Q{suit}")
        cards.append(f"K{suit}")

    rd.shuffle(cards)


# Deal Card
def deal_card(player, amount):
    """Add a specified number of cards to the given player."""
    for _ in range(amount):
        if not cards:
            return False
        player.hand.append(cards.pop(rd.randint(0, len(cards) - 1)))
    return True


# Clear
def clear():
    """Clears the console."""
    try:
        os.system("clear")
    except:
        pass


# Bot AI
def get_hand_score(hand):
    score = 0
    aces = 0

    for card in hand:
        value = card[:-1]
        if value in ["J", "Q", "K"]:
            score += 10
        elif value == "A":
            score += 1
            aces += 1
        else:
            score += int(value)

    for _ in range(aces):
        if score + 10 <= 21:
            score += 10

    return score


def get_visible_best_score(player, players):
    scores = [
        p.score
        for p in players
        if p is not player and p.health > 0 and not p.busted
    ]
    return max(scores, default=0)


def score_bot_choice(player, players):
    """Try to beat the best score currently visible."""
    best_score = get_visible_best_score(player, players)

    if best_score == 0:
        return "S" if player.score >= 17 else "H"

    if player.score > best_score:
        return "S"

    # If the best visible score is already 21, there is no reason to risk busting.
    if best_score >= 21:
        return "S"

    # Try to reach one point above the best visible score.
    if player.score <= best_score:
        return "H"

    return "S"


# Hi-Lo card counting:
# 2-6 = +1, 7-9 = 0, 10/J/Q/K/A = -1
def card_count_value(card):
    value = card[:-1]

    if value in ["2", "3", "4", "5", "6"]:
        return 1
    if value in ["10", "J", "Q", "K", "A"]:
        return -1
    return 0


def count_dealt_cards():
    # The cards remaining in the deck are known to the game, but the bot
    # only sees cards that have already been dealt, just like a player would.
    # Since every round uses a fresh deck, this count resets every round.
    seen = []
    for p in players:
        seen.extend(p.hand)

    return sum(card_count_value(card) for card in seen)


def counting_bot_choice(player, players):
    """Beat the best visible score while adjusting risk using a running count."""
    best_score = get_visible_best_score(player, players)
    running_count = count_dealt_cards()

    if best_score == 0:
        best_score = 17

    if player.score > best_score:
        return "S"

    # A positive count means more low cards have appeared, leaving relatively
    # more high cards in the deck. Be more conservative because a hit is
    # more likely to produce a large card.
    if running_count >= 3 and player.score >= 16:
        return "S"

    # A negative count means more high cards have appeared, leaving relatively
    # more low cards. Take additional risks when trying to catch the leader.
    if running_count <= -3 and player.score < 20:
        return "H"

    if player.score <= best_score:
        return "H"

    return "S"


def risktaker_bot_choice(player):
    """Always try to reach 20 or 21."""
    return "S" if player.score >= 20 else "H"



def defensive_bot_choice(player, players, is_first):
    """Protect HP, especially when going first or when close to death."""
    best_score = get_visible_best_score(player, players)

    if is_first:
        # Normally settle at 15 when there is no information from opponents.
        # He doesn't believe people are lucky: if a single hit would kill him,
        # he tries to reach a score that should survive a normal winning hit.
        if player.health < 20:
            survival_score = 20 - player.health
            survival_score = max(15, survival_score)

            if player.score >= survival_score:
                return "S"
            return "H"

        if player.score >= 15:
            return "S"

        return "H"

    if best_score == 0:
        return "S" if player.score >= 17 else "H"

    if player.score > best_score:
        return "S"

    # Standing loses by best_score - current_score; busting loses by best_score.
    # Prefer the cheap loss when the current score is already reasonably safe,
    # especially when HP is getting low. Otherwise use the score strategy.
    stand_damage = best_score - player.score
    bust_damage = best_score
    low_hp = player.health <= 25

    if stand_damage < bust_damage and (player.score >= 12 or low_hp):
        return "S"

    return score_bot_choice(player, players)



def gpt_bot_choice(player, players, is_first):
    """
    Play like a human strategist: prioritize winning without unnecessary risk.

    The bot only uses information available in the current game state:
    own score/HP, opponents' visible scores/HP, and turn order.
    It does not inspect or infer other bots' hidden archetypes.
    """
    opponents = [
        p
        for p in players
        if p is not player and p.health > 0 and not p.busted
    ]

    visible_scores = [p.score for p in opponents]
    best_score = max(visible_scores, default=0)
    lowest_opponent_hp = min((p.health for p in opponents), default=100)

    # If nobody has a meaningful visible score yet, use a solid baseline.
    if best_score == 0:
        if player.score >= 17:
            return "S"
        return "H"

    # Already winning: don't throw away a winning position.
    if player.score > best_score:
        return "S"

    # 21 is already the strongest normal score. Don't risk a bust.
    if player.score >= 21:
        return "S"

    # If we are behind and need the round, keep pushing.
    if player.score < best_score:
        # A healthy player can afford to chase a close deficit.
        if player.score < 17:
            return "H"

        # At 17-19, only keep pushing when the deficit actually matters.
        # A very low-HP opponent is already vulnerable, so avoid unnecessary
        # risk when a small loss would still leave us in a good position.
        if lowest_opponent_hp <= 15 and player.score >= best_score - 1:
            return "S"

        return "H"

    # Tied with the best visible score: standing secures the tie unless
    # there is a compelling reason to improve the position.
    if player.score >= 17:
        return "S"

    return "H"

def copycat_bot_choice(player, players, previous_bot):
    """Copy the target's number of hits, then stand if still alive."""
    target = players[0] if players[0] is not player else previous_bot

    if target is None:
        return rd.choice(["H", "S"])

    target_hits = getattr(target, "hits_this_round", 0)

    if player.hits_this_round < target_hits:
        return "H"

    return "S"


def noob_bot_choice(player):
    """Randomly decide whether to hit or stand."""
    return rd.choice(["H", "S"])


def average_bot_choice(player):
    """Play simply: hit below 17 and stand at 17 or better."""
    return "S" if player.score >= 17 else "H"


# Bot roster
# Add new bot archetypes here later. The game draws from this roster and
# avoids duplicates until every archetype has been used once.
BOT_ROSTER = {
    "score": "score",
    "counter": "counter",
    "defensive": "defensive",
    "gpt": "gpt",
    "average": "average",
    "noob": "noob",
    "copycat": "copycat",
    "risktaker": "risktaker",
}

BOT_LABELS = {
    "score": "score bot",
    "counter": "counter",
    "defensive": "defensive bot",
    "gpt": "GPT",
    "average": "Average bot",
    "noob": "Noob",
    "copycat": "Copycat",
    "risktaker": "Risktaker",
}


# Players
player_name = input("What's your name? ").strip() or "Nyther"

# If the player chooses a name already reserved for a bot, keep the player's
# chosen name and give the bot the familiar "the second" variant.
player_name_lower = player_name.casefold()

while True:
    try:
        opponent_count = int(input("How many opponents? (1-3) "))
        if 1 <= opponent_count <= 3:
            break
    except ValueError:
        pass
    print("Please enter a number between 1 and 3.")

available_bot_names = BOT_NAMES.copy()
rd.shuffle(available_bot_names)

# If the player picked a reserved bot name, the player gets the "the second"
# treatment. The bot keeps the original name: the player is the side bitch.
if player_name_lower in {name.casefold() for name in available_bot_names}:
    player_name = f"{player_name} the second"
    player_name_lower = player_name.casefold()

bot_names = []
used_names = {player_name_lower}

for _ in range(opponent_count):
    if available_bot_names:
        name = available_bot_names.pop()

        # A bot name can still collide with a player's "the second" name.
        if name.casefold() in used_names:
            name = f"{name} the second"
    else:
        # If the configurable name list is exhausted, create a relation to
        # an existing name.
        base_name = rd.choice(bot_names) if bot_names else "Bot"
        suffix = rd.choice(NAME_SUFFIXES)
        name = f"{base_name}{suffix}"

    while name.casefold() in used_names:
        base_name = name
        name = f"{base_name}{rd.choice(NAME_SUFFIXES)}"

    bot_names.append(name)
    used_names.add(name.casefold())

players = [Player(player_name)] + [Player(name) for name in bot_names]

# Build a game-specific roster. Each archetype is preferred only once before
# duplicates are allowed.
available_types = list(BOT_ROSTER.values())
bot_ai = {}

for p in players[1:]:
    if not available_types:
        available_types = list(BOT_ROSTER.values())

    bot_type = rd.choice(available_types)
    available_types.remove(bot_type)
    bot_ai[p] = bot_type

# First round starts in a random order. After that, the previous round's winner
# goes first.
round_order = players.copy()
rd.shuffle(round_order)

# Game
while game:
    new_deck()

    # Reset round state; dead players cannot carry stale state into later rounds.
    for p in players:
        p.score = 0
        p.busted = p.health <= 0
        p.clear_hand()

    print("Players: " + " ".join([f"[{p.name} : DEAD]" if p.health <= 0 else f"[{p.name} : {p.health}HP]" for p in players]))
    print()

    # Cycle players in the current round order
    for player in round_order:
        if player.health <= 0:
            continue

        play = True
        player.clear_hand()
        player.busted = False
        player.hits_this_round = 0

        if not deal_card(player, 2):
            break

        print(f"{player.name}'s turn: [{player.health}HP]")

        # Player Round
        while play:

            # Score count
            player.score = get_hand_score(player.hand)

            # Turn Start
            print(f"{player.name}: {', '.join(player.hand)} = {player.score}")

            # Lose check
            if player.score > 21:
                player.busted = True
                player.score = 0
                print(f"{player.name} has busted!\n")
                sleep(1)
                break

            choice = ""

            # User Choice
            if player is players[0]:
                while True:
                    choice = input("> Hit or Stand? ").upper()
                    if choice in ["H", "S", "HIT", "STAND"]:
                        break

            # Bot Choice
            else:
                previous_bot = None
                for prior_player in round_order:
                    if prior_player is player:
                        break
                    if prior_player is not players[0] and prior_player.health > 0:
                        previous_bot = prior_player

                is_first = not any(
                    prior_player is not player and prior_player.health > 0
                    for prior_player in round_order
                    if prior_player is not players[0]
                )

                if bot_ai[player] == "score":
                    choice = score_bot_choice(player, players)
                elif bot_ai[player] == "counter":
                    choice = counting_bot_choice(player, players)
                elif bot_ai[player] == "defensive":
                    choice = defensive_bot_choice(player, players, is_first)
                elif bot_ai[player] == "gpt":
                    choice = gpt_bot_choice(player, players, is_first)
                elif bot_ai[player] == "average":
                    choice = average_bot_choice(player)
                elif bot_ai[player] == "noob":
                    choice = noob_bot_choice(player)
                elif bot_ai[player] == "copycat":
                    choice = copycat_bot_choice(player, players, previous_bot)
                elif bot_ai[player] == "risktaker":
                    choice = risktaker_bot_choice(player)
                else:
                    choice = noob_bot_choice(player)

                sleep(rd.uniform(1.2, 1.8))

            if choice in ["H", "HIT"]:
                player.hits_this_round += 1
                if not deal_card(player, 1):
                    print("The deck is empty. Ending the round.")
                    break

            elif choice in ["S", "STAND"]:
                print(f"{player.name} has decided to stand.")
                if player.score == 21:
                    player.score *= 2
                print()
                sleep(1)
                break

    # All lose = draw, considering active players only
    active_players = [p for p in players if p.health > 0]
    busts = [player.busted for player in active_players]
    winners = []

    if not active_players or sum(busts) == len(active_players):
        print("No one won the round...")

    else:
        podium = sorted(
            active_players,
            key=lambda player: player.score if not player.busted else 0,
            reverse=True
        )
        winners = [p for p in podium if p.score == podium[0].score]

        if len(winners) > 1:
            draw_winners = [p.name for p in winners]
            print(f"{', '.join(draw_winners[:-1]) + ' and ' + draw_winners[-1]} got a Draw!")
        elif len(winners) == 1:
            print(f"{winners[0].name} won the round!")

        # Damage to losers
        for p in active_players:
            for w in winners:
                if p is w or p in winners:
                    continue

                damage = w.score - p.score
                p.health = max(p.health - damage, 0)

                print(f"{w.name} hit {p.name} for {damage} damage.")

                if p.health <= 0:
                    print(f"{p.name} is dead!")

    # Game check
    survivors = [p for p in players if p.health > 0]

    if len(survivors) == 1:
        print()
        print(f"{survivors[0].name} has won the game!")
        bot_descriptions = [
            f"{p.name} was the {BOT_LABELS.get(bot_ai[p], bot_ai[p])}"
            for p in players[1:]
        ]
        if bot_descriptions:
            print(", ".join(bot_descriptions) + ".")
        game = False

    else:
        # A round winner gets first position next round. If the round is a draw,
        # keep the current order rather than giving an arbitrary player priority.
        if winners:
            round_order = winners + [
                p for p in round_order
                if p not in winners and p.health > 0
            ]

        next_turn = [p.name for p in round_order if p.health > 0]
        if next_turn:
            print(f"Next round: {next_turn[0]} goes first.")

        input("...")
        clear()
