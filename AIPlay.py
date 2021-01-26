import numpy as np
from model import Actions
from ActionHash import ActionHash
from keras.models import load_model

def AIPlay(game):
    observation_space = len(Actions(game).state)
    actionhash = ActionHash()
    model = load_model('model/model.h5')
    state = Actions(game).state
    state = np.reshape(state, [1, observation_space])
    q_values = model.predict(state)
    q_hashed = {i:q for i,q in enumerate(q_values[0]) if (actionhash.get(i) != 'LR') | (not game.last_move_lock_n_roll)}
    while True:
        choice_idx = [i for i,v in q_hashed.items() if v == np.max(list(q_hashed.values()))][0]
        choice = actionhash.get(choice_idx)

        if (len(game.dice) > 0) & (len([i for i in game.board if i.isnumeric]) > 0):
            pos = int(choice.split('_')[1])
            next_die = game.dice[0]
            if game.board[pos].isnumeric():
                game.place_die(next_die,pos+1)
                print(f'the AI has chosen to play die {next_die} to space {pos+1}')
                return
            elif (game.jokers > 0) & (pos not in game.joker_on_board):
                game.place_joker(pos+1)
                print(f'the AI has chosen to place a joker on space {pos+1}')
                return
            else:
                q_hashed.pop(choice_idx) # go to next-best move
        else:
            game.lock_n_roll()
            if game.gameover:
                print('the AI apologizes for losing')
            else:
                print("the AI has chosen to Lock N' Roll my dude/dudette!")
            return


