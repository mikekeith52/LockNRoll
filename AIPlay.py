import numpy as np
from model import AVActions
from ActionHash import ActionHash
from keras.models import load_model

def AIPlay(game):
    observation_space = len(AVActions(game).state)
    actionhash = ActionHash()
    model = load_model('model/model.h5')
    state = AVActions(game).state
    state = np.reshape(state, [1, observation_space])
    available_actions = AVActions(game).available
    q_values = model.predict(state)
    q_hashed = {i:q for i,q in enumerate(q_values[0]) if actionhash.get(i) in available_actions}
    chosen_action = actionhash.get([i for i,v in q_hashed.items() if v == np.max(list(q_hashed.values()))][0])

    if chosen_action[0] == 'JO':
        game.place_joker(chosen_action[1]+1)
        print(f'the AI chose to place a joker on space {chosen_action[1]+1}')
        return
    elif chosen_action == ('LO','RO'):
        game.lock_n_roll()
        if not game.gameover:
            print("the AI has chosen to Lock N' Roll!")
            return
        else:
            print("the AI apologizes for losing the game")
            return
    else:
        game.place_die(chosen_action[0],chosen_action[1]+1)
        print(f'the AI chose to play die {chosen_action[0]} to space {chosen_action[1]+1}')
        return


