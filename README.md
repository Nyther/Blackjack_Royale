# Blackjack
Terminal based game of Blackjack with a few twists.  
Inspired by the game Dungeons & Degenerate Gamblers.

## Quirks:
- Game is played against simple "bots".
- Bots have a random target score set for themselves at the start of each game.
- Each player has health, instead of betting money they are waging with their lives.
- The winner of a round deals damage to all losers equals to the difference in their hand score and gets to play first next round.
- Scoring 21 deals double damage (42).
- Busting sets your score to 0 essentially taking full damage.
- Aces can be worth 1 or 11 based on the score context.
- The game is played with a simulated deck, that means card counting is a possible strategy. Althought it gets "shuffled" each round.

## Future Plans:
- Have one random bot play smartly by analysing other player's score and picking a target score accordingly.
- Have one random bot play as a cheater by not only analysing other player's score but also do card counting.
