import numpy as np
from model import AVActions
from ActionHash import ActionHash
from keras.models import load_model

def AIPlay(game):
    observation_space = len(AVActions(game).state)
    action_space = ActionHash().__len__()
    model = load_model('model/model.h5')
    state = AVActions(game).state
    state = np.reshape(state, [1, observation_space])
    available_actions = AVActions(game).available
    q_values = model.predict(state)
    q_hashed = {} # chaining hash table
    for i, v in enumerate(q_values[0]):
        if v not in q_hashed:
            q_hashed[v] = [i]
        else:
            q_hashed[v].append(i)
    q_sorted = sorted(q_values[0])[::-1] # rate all actions best-to-worst
    for q in q_sorted: # iterate until you find the best available action
        for i in q_hashed[q]:
            if ActionHash().get(i) in available_actions:
               chosen_action = ActionHash().get(i)

    if chosen_action[0] == 'JO':
        game.place_joker(chosen_action[1]+1)
    else:
        game.place_die(chosen_action[0],chosen_action[1]+1)

    print(f'the AI chose to play die {chosen_action[0]} to space {chosen_action[1]+1}')


