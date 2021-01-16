import numpy as np

colors_pool = ['R','Y','G','B']
numbers_pool = ['1','2','3','4']

init_board = ['01','02','03','04',
              '05','06','07','08',
              '09','10','11','12',
              '13','14','15','16']

board_graph_rep ="""==================
||{}||{}||{}||{}||
==================
||{}||{}||{}||{}||
==================
||{}||{}||{}||{}||
==================
||{}||{}||{}||{}||
=================="""

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

class GameError(Exception):
	class BoardPosNotEmpty(Exception):
		pass
	class DieDoesNotExist(Exception):
		pass
	class JokerNotAvailable(Exception):
		pass

class Game:
	def __init__(self):
		self.board = init_board[:]
		self.dice = [c+n for c,n in zip(np.random.choice(colors_pool,size=4),np.random.choice(numbers_pool,size=4))][:]
		#self.dice = ['R1','R2','R3','R4']
		self.jokers = 0
		self.next_joker = 250 # points until the next joker (this will change as you gain points)
		self.next_joker_points = 250 # total points until the next joker (this won't change until self.joker goes under 0, then it will increase or stay the same)
		self.next_joker_bonus = 1000 # if you have two jokers and earn another, this is how many points will be awarded to you
		self.index_not_scored = combination_idx[:] # a list of indices representing board combos that can be evaluated on your next lock n' roll
		                                           # elements of this list are deleted and re-added depending on parts of the board that have already been scored/opened back up after a clear
		self.points = 0 # your total score
		self.gameover = False

	def _score_combo(self,combo):
		def points(score_key):
			return int(round(score_index[score_key][0]*.75**(len([i for i in combo if i == 'JO']))))

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
		# same color same number
		if ((len(unq_color) == 1) & (len(unq_number) == 1)) | ((len(unq_color) == 2) & (len(unq_number) == 2) & ('JO' in unq_dice)):
			print('{combo} combo netted you {points} points'.format(combo=combo,points=points('scsn')))
			return score_index['scsn']
		# same color different number
		elif ((len(unq_color) == 1) & (len(unq_number) == 4)) | ((len(unq_color) == 2) & (len(unq_number) == 4) & ('JO' in unq_dice)):
			print('{combo} combo netted you {points} points'.format(combo=combo,points=points('scen')))
			return score_index['scen']
		# same number different color
		elif ((len(unq_color) == 4) & (len(unq_number) == 1)) | ((len(unq_color) == 4) & (len(unq_number) == 2) & ('JO' in unq_dice)):
			print('{combo} combo netted you {points} points'.format(combo=combo,points=points('ecsn')))
			return score_index['ecsn']
		# different number different color
		elif ((len(unq_color) == 4) & (len(unq_number) == 4)):
			print('{combo} combo netted you {points} points'.format(combo=combo,points=points('ecen')))
			return score_index['ecen']
		# two pair
		elif ((len(unq_color) == 2) & (len(unq_number) == 2) & (unq_dice == 2)) | ((len(unq_color) == 3) & (len(unq_number) == 3) & (unq_dice == 3) & ('JO' in unq_dice)):
			print('{combo} combo netted you {points} points'.format(combo=combo,points=points('tp')))
			return score_index['tp']
		# same color only
		elif (len(unq_color) == 1) | ((len(unq_color) == 2) & ('JO' in unq_dice)):
			print('{combo} combo netted you {points} points'.format(combo=combo,points=points('sc')))
			return score_index['sc']
		# same number only
		elif (len(unq_number) == 1) | ((len(unq_number) == 2) & ('JO' in unq_dice)):
			print('{combo} combo netted you {points} points'.format(combo=combo,points=points('sn')))
			return score_index['sn']
		# pair color pair number
		elif ((len(unq_color) == 2) & (len(unq_number) == 2)) | ((len(unq_color) == 3) & (len(unq_number) == 3) & ('JO' in unq_dice)):
			print('{combo} combo netted you {points} points'.format(combo=combo,points=points('pcpn')))
			return score_index['pcpn']
		# each color only
		elif (len(unq_color) == 4):
			print('{combo} combo netted you {points} points'.format(combo=combo,points=points('ec')))
			return score_index['ec']
		# each number only
		elif (len(unq_number) == 4):
			print('{combo} combo netted you {points} points'.format(combo=combo,points=points('en')))
			return score_index['en']
		# pair color
		elif (len(unq_color) == 2) | ((len(unq_color) == 3) & ('JO' in unq_dice)):
			print('{combo} combo netted you {points} points'.format(combo=combo,points=points('pc')))
			return score_index['pc']
		# pair number
		elif (len(unq_number) == 2) | ((len(unq_number) == 3) & ('JO' in unq_dice)):
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
		if which in self.dice:
			if isinstance(where,int):
				if self.board[where-1].isnumeric():
					if where == int(self.board[where-1]):
						self.board[where-1] = which
						for i, d in enumerate(self.dice):
							if d == which:
								del self.dice[i]
								break
					else:
						raise GameError.BoardPosNotEmpty(f'Space {where} is not available')
				else: 
					raise GameError.BoardPosNotEmpty(f'Space {where} is not available')
		else:
			raise GameError.DieDoesNotExist(f'That die ({which}) not available')

	def place_joker(self,where):
			if self.jokers > 0:
				self.board[where-1] = 'JO'
				self.jokers -= 1
			else:
				raise GameError.JokerNotAvailable(f'joker not avaialable, earn {self.next_joker} more non-bonus points for next one')

	def score_board(self):
		bonus_points = 0
		delete_idx = [] # keeps track of indices that will need to not be evaluated again because they were already scored
		add_idx = [] # keeps track of indices that will need to be added back to self.index_not_scored based on spaces on the board that open back up
		clear_spaces = [] # keeps track of all the spaces that need to be cleared after this turn
		for idx,combo in enumerate(self.index_not_scored): # combo ex: [0,1,2,3]
			board_combo = [self.board[v] for v in combo if not self.board[v].isnumeric()] # ex: ['R1','R2','R3','R4']
			if len(board_combo) == 4:
				points_clear = self._score_combo(board_combo)
				points = int(round(points_clear[0]*.75**len([i for i in board_combo if i == 'JO'])))
				clear = points_clear[1]
				self.points += points
				if clear:
					for i in combo:
						clear_spaces.append(i)
						for ci in combination_idx:
							if i in ci:
								add_idx.append(ci) # brings back any squares that have been unlocked with the clear
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

		# evaluates spaces cleared to grant bonus points
		spaces_cleared = len(clear_spaces)
		if spaces_cleared > 4:
			spaces_cleared -= 4
			bonus_points += spaces_cleared*50
		if bonus_points > 0:
			print(f'bonus points scored: {bonus_points}')
			self.points += bonus_points

	def get_new_dice(self):
		number_new_dice = min(4,len([v for v in self.board if v.isnumeric()]))
		if (number_new_dice == 0) & (self.jokers == 0):
			self.game_over()
		self.dice = [c+n for c,n in zip(np.random.choice(colors_pool,size=4),np.random.choice(numbers_pool,size=number_new_dice))][:]
		#self.dice = ['R1','R2','R3','R4']

	def game_over(self):
		print(f'game over! your final score is: {self.points}')
		self.gameover = True

