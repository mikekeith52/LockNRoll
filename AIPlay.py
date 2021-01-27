import numpy as np
from State import State
from keras.models import load_model

def AIPlay(game):
    observation_space = len(State(game).state)
    model = load_model('model/model.h5')
    state = State(game).state
    state = np.reshape(state, [1, observation_space])
    q_values = model.predict(state)
    q_hashed = {i:q for i,q in enumerate(q_values[0])}
    while True:
        choice = [i for i,v in q_hashed.items() if v == np.max(list(q_hashed.values()))][0]

        if (len(game.dice) > 0) & (len([i for i in game.board if i.isnumeric()]) > 0):
            next_die = game.dice[0]
            if game.board[choice].isnumeric():
                game.place_die(next_die,choice+1)
                print(f'the AI has chosen to play die {next_die} to space {choice+1}')
                return
            elif (game.jokers > 0) & (choice not in game.joker_on_board):
                game.place_joker(choice+1)
                print(f'the AI has chosen to place a joker on space {choice+1}')
                return
            else:
                q_hashed.pop(choice) # go to next-best move
        else:
            game.lock_n_roll()
            if game.gameover:
                print('the AI apologizes for losing')
            else:
                print("the AI has chosen to Lock N' Roll my dude/dudette!")
            return


