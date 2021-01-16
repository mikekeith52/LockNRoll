import game

g = game.Game()

while not g.gameover:
	print('Score:',g.points)
	g.print_board()
	print('Dice\n',g.dice)
	print('Jokers\n',g.jokers)
	move = input("""what move do you want to play:
	0: readme
	1: place die (which,where)
	2: place joker (where)
	3: lock n' roll
	4: see empty board (useful to reference when attempting to place a joker)
	5: exit
selection: """)
	try:
		if len(move) == 0:
			continue
		elif move == '0':
			print(open('README.md','r').read())
		elif move[0] == '1':
			which_where = tuple(move[2:].split(','))
			g.place_die(which_where[0],int(which_where[1]))
		elif move[0] == '2':
			g.place_joker(int(move[2:]))
		elif move == '3':
			g.score_board()
			if len(g.dice) == 0:
				g.get_new_dice()
		elif move == '4':
			g.print_init_board()
		elif move == '5':
			print('exiting...')
			break
		else:
			print('invalid entry, make sure your casing is correct')
	except (game.GameError.BoardPosNotEmpty,game.GameError.DieDoesNotExist,game.GameError.JokerNotAvailable) as e:
		print(e)