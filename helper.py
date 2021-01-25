import game

def score_last_move(g,last_move):
	points = 0
	for idx,combo in enumerate(game.combination_idx): # combo ex: [0,1,2,3]
		board_combo = [g.board[v] for v in combo if not g.board[v].isnumeric()] # ex: ['R1','R2','R3','R4']
		if (len(board_combo) == 4) & (last_move[0] in board_combo) & (last_move[1] in combo):
			points += int(round(g._score_combo(board_combo)[0]*.75**(board_combo.count('JO'))))

	return points