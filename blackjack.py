import random as rd
import os
from time import  sleep

suits = ["♤", "♧", "♡", "◇"]
cards = []
game = True
play = True


# Player
class Player:
	def __init__(self, name : str):
		self.name : str = name
		self.hand : list = []
		self.score : int = 0
		self.busted : bool = True
		self.health : int = 100
		self.target : int = rd.randint(16,21)
		
	def clear_hand(self):
		"""
		Empties the player's hand by clearing the list.
		"""
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
	"""
	Add a specified number of cards to the given player.
	"""
	for _ in range(amount):
		if not cards:
			return False
		player.hand.append(cards.pop(rd.randint(0, len(cards) - 1)))
	return True
		
# Clear
def clear():
	"""
	Clears the console.
	"""
	try:
		os.system("clear")
	except:
		pass

# Players
player_names = ["Nyther", "X0R", "Connor", "Zeee"]
players = [Player(name) for name in player_names]

# First round starts in a random order. After that, the previous round's winner goes first.
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

	print("Players: " + " ".join([f"[{p.name} : {p.health}HP]" for p in players]))
	print(f"Turn order: {' -> '.join(p.name for p in round_order if p.health > 0)}")
	print()

	# Cycle players in the current round order
	for player in round_order:
		if player.health <= 0:
			continue
			
		play = True
		player.clear_hand()
		player.busted = False
		if not deal_card(player, 2):
			break
		print(f"{player.name}'s turn: [{player.health}HP]")
	
		# Player Round
		while play:
			
			# Score count
			player.score = 0
			hand_values = [c[:-1] for c in player.hand]
			for card in hand_values:
				card = card.replace("J", "10").replace("Q", "10").replace("K", "10").replace("A", "1")
				player.score += int(card)
			
			for _ in range(hand_values.count("A")):
				if player.score + 10 <= 21:
					player.score += 10
			
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
				if player.score >= player.target or all(p.busted for p in players if p is not player and p.health > 0): # Stands if everyone else active has busted
					choice = "S"
				else:
					choice = "H"
				sleep(1.5)
				
			if choice in ["H", "HIT"]:
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
		podium = sorted(active_players, key = lambda player: player.score if not player.busted else 0, reverse = True)
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
		game = False
	else:
		# A round winner gets first position next round. If the round is a draw,
		# keep the current order rather than giving an arbitrary player priority.
		if winners:
			round_order = winners + [p for p in round_order if p not in winners and p.health > 0]
		input("...")
		clear()
	
