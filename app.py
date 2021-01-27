import game
welcome = r"""
=========================================================================================================
=========================================================================================================
||\\||\\||  ||     //====\\ //==== || //   ||\\   ||//   //==\\ //====\\ ||     ||      || ||  ||//||//||
||\\||\\||  ||     ||    || ||     ||//    || \\  ||     ||  // ||    || ||     ||      || ||  ||//||//||
||\\||\\||  ||     ||    || ||     ||\\    ||  \\ ||     ||==   ||    || ||     ||      || ||  ||//||//||
||\\||\\||  ||==== \\====// \\==== || \\   ||   \\||     ||  \\ \\====// ||==== ||====  <> <>  ||//||//||
=========================================================================================================
=========================================================================================================
"""
interface = """what move do you want to play?
  0: readme
  1: place die (which,where)
  2: place joker (where)
  3: lock n' roll
  4: see empty board (useful to reference when attempting to place a joker)
  5: let the AI play
  6: exit
selection: """

class main:
	def __init__(self):
		print(welcome)

	def run(self):
		g = game.Game()
		while not g.gameover:
			print('Score:',g.points)
			g.print_board()
			print('Dice\n',g.dice)
			print('Jokers\n',g.jokers)
			move = input(interface)
			try:
				if len(move) == 0:
					continue
				elif move == '0':
					print(open('README.md','r').read())
				elif move[0] == '1':
					which_where = tuple(move[2:].upper().split(','))
					g.place_die(which_where[0],which_where[1])
				elif move[0] == '2':
					g.place_joker(move[2:])
				elif move == '3':
					g.lock_n_roll()
				elif move == '4':
					g.print_init_board()
				elif move == '5':
					from AIPlay import AIPlay
					AIPlay(g)
				elif move == '6':
					g.game_over()
				elif move == 'mk17':
					from monitor import get_state
					get_state(g)
				else:
					print('invalid entry')
			except (game.GameError,IndexError) as e:
				print(e)

if __name__ == '__main__':
	app = main()
	app.run()