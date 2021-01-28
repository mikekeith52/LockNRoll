import numpy as np
from State import State, StateReducedLDA, ReducedObsSpaceLDA
from keras.models import load_model

model = load_model('model/model.h5')

def AIPlay(game):
    observation_space = ReducedObsSpaceLDA
    state = StateReducedLDA(State(game)).state
    state = np.reshape(state, [1, observation_space])
    q_values = model.predict(state)
    action = np.argmax(q_values[0])

    if ((len(game.dice) > 0) & (len([i for i in game.board if i.isnumeric()]) > 0)) | (game.jokers > 0):
        if game.board[action].isnumeric():
            next_die = game.dice[0]
            game.place_die(next_die,action+1)
            print(f'the AI has placed {next_die} on space {action+1}')
        elif (len([i for i in game.board if i.isnumeric()]) > 0) & (len(game.dice) > 0):
            next_die = game.dice[0]
            adjusted_pos = min([int(i) for i in game.board if i.isnumeric()],key = lambda x: abs(x-(action+1)))
            game.place_die(next_die,adjusted_pos)
            print(f'the AI has placed {next_die} on space {adjusted_pos}')
        elif (game.jokers > 0) & (game.board[action] != 'JO'):
            game.place_joker(action+1)
            print(f'the AI has placed a joker on space {action+1}')
        else:
            adjusted_pos = min([int(i) for i,v in enumerate(game.board) if v != 'JO'],key = lambda x: abs(x-action))
            game.place_joker(adjusted_pos+1)
            print(f'the AI has placed a joker on space {adjusted_pos+1}')
    else:
        game.lock_n_roll()
        if game.gameover:
            print('the AI apologizes for losing')
        else:
            print("the AI has chosen to Lock N' Roll my dude/dudette!")


