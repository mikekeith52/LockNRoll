def evaluate_reward(game_state,action):
    init_points = game_state.points
    init_open_spaces = sum([1 for i in game_state.board if i.isnumeric()])
    choice = ActionHash().get(action)

    try:
        if choice[0] == 'JO':
            game_state.place_joker(choice[1] + 1)
            return score_last_move(game_state,choice) # to teach it that it's better to play a die rather than lock n roll when there will be no points gained
        elif choice != ('LO','RO'):
            game_state.place_die(choice[0],choice[1] + 1)
            return score_last_move(game_state,choice) # to teach it that it's better to play a die rather than lock n roll when there will be no points gained
    except (game.GameError.BoardPosNotEmpty,game.GameError.DieDoesNotExist,game.GameError.JokerNotAvailable,game.GameError.JokeronJoker): # in case you try a move you can't do -- this should be knowable with the state and the AI needs to learn it
        return -1000 # so it can learn which moves are invalid - invalid moves must be worse than accepting a game over

    if choice == ('LO','RO'):
        if game_state.last_move_lock_n_roll:
            game_state.lock_n_roll()
            return -1000 # to stop it from locknroll over and over instead of game over
        game_state.lock_n_roll()
    if game_state.gameover:
        return - 100
    else:
        open_spaces = sum([1 for i in game_state.board if i.isnumeric()])
        spaces_cleared = open_spaces - init_open_spaces
        if (spaces_cleared == 0) & (len(game_state.dice) > 0):
            return -1000
        else:
            return spaces_cleared*100


def evaluate_reward(game_state,action):
    init_points = game_state.points
    choice = ActionHash().get(action)

    try:
        if choice[0] == 'JO':
            game_state.place_joker(choice[1] + 1)
            return score_last_move(game_state,choice) # to teach it that it's better to play a die rather than lock n roll when there will be no points gained
        elif choice != ('LO','RO'):
            game_state.place_die(choice[0],choice[1] + 1)
            return score_last_move(game_state,choice) # to teach it that it's better to play a die rather than lock n roll when there will be no points gained
    except (game.GameError.BoardPosNotEmpty,game.GameError.DieDoesNotExist,game.GameError.JokerNotAvailable,game.GameError.JokeronJoker): # in case you try a move you can't do -- this should be knowable with the state and the AI needs to learn it
        return -1000 # so it can learn which moves are invalid - invalid moves must be worse than accepting a game over

    if choice == ('LO','RO'):
        if game_state.last_move_lock_n_roll: # to stop it from thinking it can do this over and over to avoid game overs
            return -1000
        game_state.lock_n_roll()
    if game_state.gameover:
        return (game_state.points - init_points - 900)
    else:
        return (game_state.points - init_points)