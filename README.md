# Blackjack
Terminal based game of Blackjack with a few twists.  
Inspired by the game Dungeons & Degenerate Gamblers.

## Quirks:
- Game is played against "bots".
- There are many types of bots each with their own strategy that are only revealed at the end of a game.
- Each player has health, instead of betting money they are waging with their lives.
- The winner of a round deals damage to all losers equals to the difference in their hand score and gets to play first next round.
- Scoring 21 deals double damage (42).
- Busting sets your score to 0 essentially taking full damage.
- Aces can be worth 1 or 11 based on the score context.
- The game is played with a simulated deck, that means card counting is a possible strategy. Althought it gets "shuffled" each round.

## Bot Archetypes: **[SPOILERS]**

- **Score Bot** — Tries to beat the highest visible opponent score and stands when already ahead.
- **Counter Bot** — Uses visible scores and Hi-Lo card counting to decide when to hit or stand.
- **Defensive Bot** — Prioritizes survival and minimizing HP loss over achieving a high score.
- **GPT** — Uses a calculated, human-like strategy based only on the current game state, balancing score, HP, and risk. It has no knowledge of other bots' identities or strategies.
- **Average Bot** — Uses a simple Blackjack-style strategy: hit below 17 and stand at 17 or higher.
- **Noob** — Randomly chooses whether to hit or stand.
- **Copycat** — Mimics another player's number of hits, then stands if it survives.
- **Risktaker** — Always pushes for 20 or 21, regardless of the risk of busting.
