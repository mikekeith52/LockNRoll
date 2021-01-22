from numpy import random

# to form the dice, the following two lists are drawn from randomly
colors_pool = ['R','Y','G','B']
numbers_pool = ['1','2','3','4']

# the board is 1-indexed (no good reason for that)
init_board = ['01','02','03','04',
              '05','06','07','08',
              '09','10','11','12',
              '13','14','15','16']

# this is the command-line graphical representation of the board
board_graph_rep ="""==================
||{}||{}||{}||{}||
==================
||{}||{}||{}||{}||
==================
||{}||{}||{}||{}||
==================
||{}||{}||{}||{}||
=================="""

# these are the indices of the board that can be scored
combination_idx = [
	[0,1,2,3],
	[4,5,6,7],
	[8,9,10,11],
	[12,13,14,15],
	[0,4,8,12],
	[1,5,9,13],
	[2,6,10,14],
	[3,7,11,15],
	[0,3,12,15],
	[0,5,10,15],
	[3,6,9,12],
	[0,1,4,5],
	[1,2,5,6],
	[2,3,6,7],
	[4,5,8,9],
	[5,6,9,10],
	[6,7,10,11],
	[8,9,12,13],
	[9,10,13,14],
	[10,11,14,15]
]

# descriptive errors
class GameError(Exception):
	class BoardPosNotEmpty(Exception):
		pass
	class DieDoesNotExist(Exception):
		pass
	class JokerNotAvailable(Exception):
		pass
	class JokeronJoker(Exception):
		pass

# the game class
class Game:
	def __init__(self,quiet=False):
		self.quiet = quiet
		self.board = init_board[:]
		self.dice = [c+n for c,n in zip(random.choice(colors_pool,size=4),random.choice(numbers_pool,size=4))][:]
		#self.dice = ['R1','R2','R3','R4']
		self.jokers = 0
		self.next_joker = 250 # points until the next joker (this will change as you gain points)
		self.next_joker_points = 250 # total points until the next joker (this won't change until self.joker goes under 0, then it will increase or stay the same)
		self.next_joker_bonus = 1000 # if you have two jokers and earn another, this is how many points will be awarded to you
		self.index_not_scored = combination_idx[:] # a list of indices representing board combos that can be evaluated on your next lock n' roll
		                                           # elements of this list are deleted and re-added depending on parts of the board that have already been scored/opened back up after a clear
		self.joker_on_board = [] # to fix issue where jokers in an un-cleared combo get scored over and over
		self.points = 0 # your total score
		self.gameover = False
		self.moves = 0
		
	def _score_combo(self,combo):
		""" combo is a list of dice to be scored (ex: ["R1","B2","G3","Y4"])
		"""
		def points(score_key):
			""" evaluates how much the combo is worth
				to do: re-evaluate scoring with more than 1 joker
			"""
			return int(round(score_index[score_key][0]*.75**num_jokers))
		
		def one_pair(combo,idx):
			""" evaluates if the combo is a pair color or pair number
				for pair color, idx=0 (since color is first element of the dice)
				for pair number, idx=1 (since number is second element of the dice)
				only gets called if there are two unique colors/numbers in the combo
			"""
			tally = [i[idx] for i in combo]
			tally_cnts = [tally.count(i) for i in tally]
			return True if tally_cnts == [2,2,2,2] else False

		def two_pair(combo):
			""" evaluates if the combo is a two pair
				only gets called when len(unq_dice) == 2 (two unique dice in the combo)
			"""
			for d in unq_dice:
				if not (combo.count(d) == 2):
					return False
			return True

		# what everything is worth/whether to clear spaces on the board
		score_index = {
			'scsn':[400,True],
			'scen':[200,True],
			'ecsn':[200,True],
			'ecen':[100,True],
			'tp':[60,False],
			'sc':[40,False],
			'sn':[40,False],
			'pcpn':[20,False],
			'ec':[10,False],
			'en':[10,False],
			'pc':[5,False],
			'pn':[5,False]
		}

		# ce for combo evaluated, i[0] is the color, i[1] is the number
		unq_color = set([i[0] for i in combo])
		unq_number = set([i[1] for i in combo])
		unq_dice = set(combo)
		num_jokers = combo.count('JO')

		# 2 or more jokers always clears the combo
		if num_jokers == 2:
			if (len(unq_color) == 2) & (len(unq_number) == 2):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('scsn')))
				return score_index['scsn']
			elif ((len(unq_number) == 2) & (len(unq_color) == 3)) | ((len(unq_number) == 3) & (len(unq_color) == 2)):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('scen')))
				return score_index['scen']
			else:
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('ecen')))
				return score_index['ecen']
		# 3 or more jokers always results in the same color/same number combo			
		elif num_jokers >= 3:
			if not self.quiet:
				print('{combo} combo netted you {points} points'.format(combo=combo,points=points('scsn')))
			return score_index['scsn']
		# all other combos with one or no joker can be written fairly simply
		else:
			# same color same number
			if ((len(unq_color) == 1) & (len(unq_number) == 1)) | ((len(unq_color) == 2) & (len(unq_number) == 2) & ('JO' in unq_dice)):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('scsn')))
				return score_index['scsn']
			# same color different number
			elif ((len(unq_color) == 1) & (len(unq_number) == 4)) | ((len(unq_color) == 2) & (len(unq_number) == 4) & ('JO' in unq_dice)):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('scen')))
				return score_index['scen']
			# same number different color
			elif ((len(unq_color) == 4) & (len(unq_number) == 1)) | ((len(unq_color) == 4) & (len(unq_number) == 2) & ('JO' in unq_dice)):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('ecsn')))
				return score_index['ecsn']
			# different number different color
			elif ((len(unq_color) == 4) & (len(unq_number) == 4)):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('ecen')))
				return score_index['ecen']
			# two pair
			elif ((len(unq_dice) == 2) & (two_pair(combo))) | ((len(unq_dice) == 3) & ('JO' in unq_dice)):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('tp')))
				return score_index['tp']
			# same color only
			elif (len(unq_color) == 1) | ((len(unq_color) == 2) & ('JO' in unq_dice)):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('sc')))
				return score_index['sc']
			# same number only
			elif (len(unq_number) == 1) | ((len(unq_number) == 2) & ('JO' in unq_dice)):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('sn')))
				return score_index['sn']
			# pair color pair number
			elif ((len(unq_color) == 2) & (len(unq_number) == 2) & (len(unq_dice) == 4)) | ((len(unq_color) == 3) & (len(unq_number) == 3) & (len(unq_dice) == 4) & ('JO' in unq_dice)):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('pcpn')))
				return score_index['pcpn']
			# each color only
			elif (len(unq_color) == 4):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('ec')))
				return score_index['ec']
			# each number only
			elif (len(unq_number) == 4):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('en')))
				return score_index['en']
			# pair color
			elif (len(unq_color) == 2) & (one_pair(combo,0)):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('pc')))
				return score_index['pc']
			# pair number
			elif (len(unq_number) == 2) & (one_pair(combo,1)):
				if not self.quiet:
					print('{combo} combo netted you {points} points'.format(combo=combo,points=points('pn')))
				return score_index['pn']
			# everything else
			else:
				return [0,False]

	def print_board(self):
		print(board_graph_rep.format(self.board[0],self.board[1],self.board[2],self.board[3],
			                         self.board[4],self.board[5],self.board[6],self.board[7],
			                         self.board[8],self.board[9],self.board[10],self.board[11],
			                         self.board[12],self.board[13],self.board[14],self.board[15]))

	def print_init_board(self):
		print(board_graph_rep.format(init_board[0],init_board[1],init_board[2],init_board[3],
			                         init_board[4],init_board[5],init_board[6],init_board[7],
			                         init_board[8],init_board[9],init_board[10],init_board[11],
			                         init_board[12],init_board[13],init_board[14],init_board[15]))		

	def print_number_jokers(self):
		print(self.jokers)

	def place_die(self,which,where):
		""" which is a die that must be available in the self.dice list
		    where is a space on the 1-indexed board (see init_board global) and must be int-like (ex: 1, 1.0, '1', '01', ' 1') between 1 and 16
		"""
		if which in self.dice: # is the die in self.dice?
			try: where = int(where) # try to cast where to int type
			except ValueError: raise GameError.BoardPosNotEmpty(f'Space {where} is not available') # if can't cast where as an int, raise a game error
			if self.board[where-1].isnumeric(): # check if the str element in the board list is a number (ex: not 'R4'), if it is, that space is open
				if where == int(self.board[where-1]): # check if which is between 1 and 16 (valid board positions)
					self.board[where-1] = which # place which on the open space on the board
					for i, d in enumerate(self.dice):
						if d == which: # delete which from the self.dice list
							del self.dice[i]
							break # break after only one die has been deleted
				else:
					raise GameError.BoardPosNotEmpty(f'Space {where} is not available')
			else: 
				raise GameError.BoardPosNotEmpty(f'Space {where} is not available')
		else:
			raise GameError.DieDoesNotExist(f'That die ({which}) not available')
		self.moves += 1

	def place_joker(self,where):
		""" where is a space on the 1-indexed board (see init_board global) and must be int-like (ex: 1, 1.0, '1', '01', True)
		"""
		if self.jokers > 0:
			if self.board[int(where)-1] != 'JO':
				self.board[int(where)-1] = 'JO'
				self.jokers -= 1
			else:
				raise GameError.JokeronJoker('cannot place a joker on another joker!')
		else:
			raise GameError.JokerNotAvailable(f'joker not avaialable, earn {self.next_joker} more non-bonus points for next one')
		self.moves += 1

	def lock_n_roll(self):
		""" LOCK N' ROLL BRAH!!
		"""
		def check_for_jokers():
			""" checks for jokers on the board and opens up combinations that are touching the joker to be evaluated in the next score_board() call
				O(N) --> O(16) in all cases
				opted for a more complex solution (as opposed to O(1) worst-case) to improve readability and because board is small
				i might revist this
			"""
			for i, v in enumerate(self.board):
				if (v == 'JO') & (i not in self.joker_on_board): # that second condition is to make sure jokers aren't scored over and over
					for ci in combination_idx:
						if (i in ci) & (ci not in self.index_not_scored):
							self.index_not_scored.append(ci)
					self.joker_on_board.append(i)

		def score_board():
			""" scores board by checking scorable combinations (namespace combo) and the patterns on those combinations
				deletes any combinations that get scored to avoid being able to score again
				brings back combinations that touch spaces that have been cleared by a clear combination
				awards jokers/joker bonuses
				awards clearing bonuses
				checks if out of dice, and if so, gets the player more dice
				if out of dice, spcaes, and jokers, game over
			"""
			bonus_points = 0
			delete_idx = [] # keeps track of indices that will need to not be evaluated again because they were already scored
			add_idx = [] # keeps track of indices that will need to be added back to self.index_not_scored based on spaces on the board that open back up
			clear_spaces = [] # keeps track of all the spaces that need to be cleared after this turn
			# once indices have been cleared, adding a joker does not bring them back
			for idx,combo in enumerate(self.index_not_scored): # combo ex: [0,1,2,3]
				board_combo = [self.board[v] for v in combo if not self.board[v].isnumeric()] # ex: ['R1','R2','R3','R4']
				if len(board_combo) == 4:
					points_clear = self._score_combo(board_combo)
					points = int(round(points_clear[0]*.75**board_combo.count('JO')))
					clear = points_clear[1]
					self.points += points
					if clear:
						for i in combo:
							clear_spaces.append(i)
							for ci in combination_idx:
								if i in ci:
									add_idx.append(ci) # brings back any squares that have been unlocked with the clear
						self.joker_on_board = [e for e in self.joker_on_board if e != i] # combo with a joker on it cleared, no longer keep track of where the joker is
					else:
						delete_idx.append(combo) # to avoid double scoring
					self.next_joker -= points
					while self.next_joker <= 0:
						if self.jokers == 2:
							bonus_points += self.next_joker_bonus
							self.next_joker_bonus = min(self.next_joker_bonus*2,64000)
						else:
							self.jokers+=1
						
						self.next_joker_points = min(1500,self.next_joker_points+250)
						self.next_joker = self.next_joker + self.next_joker_points

			# deletes combo possibilities that have already been scored
			self.index_not_scored = [idx for idx in self.index_not_scored if idx not in delete_idx]

			# adds back combos that are possible to score again after board clears
			for idx in add_idx:
				if idx not in self.index_not_scored:
					self.index_not_scored.append(idx) 

			# clears spaces
			for i in clear_spaces:
				self.board[i] = init_board[i] 

			# if all spaces were cleared after scoring the board, it is the same as getting another joker/joker bonus
			if (len([i for i in self.board if i.isnumeric()]) == 16) & (len(clear_spaces) > 0):
				if self.jokers == 2:
					bonus_points += self.next_joker_bonus
					self.next_joker_bonus = min(self.next_joker_bonus*2,64000)
				else:
					self.jokers+=1

			# evaluates spaces cleared to grant bonus points
			spaces_cleared = len(set(clear_spaces))
			if spaces_cleared > 4:
				spaces_cleared -= 4
				bonus_points += spaces_cleared*50
			if bonus_points > 0:
				if not self.quiet:
					print(f'bonus points scored: {bonus_points}')
				self.points += bonus_points

		def get_new_dice():
			""" if you are out of dice and there are still spaces on the board, this will give you more dice
			"""
			if len(self.dice) == 0:
				number_new_dice = min(4,len([v for v in self.board if v.isnumeric()]))
				if (number_new_dice == 0) & (self.jokers == 0):
					self.game_over()
				else:
					self.dice = [c+n for c,n in zip(random.choice(colors_pool,size=number_new_dice),random.choice(numbers_pool,size=number_new_dice))][:]
					#self.dice = ['R1','R2','R3','R4']

		check_for_jokers()
		score_board()
		get_new_dice()
		self.last_move_lock_roll = True

	def game_over(self):
		""" exits the game
		"""
		if not self.quiet:
			print(f'game over! your final score is: {self.points}')
			print(f'your total moves were: {self.moves}')
		self.gameover = True