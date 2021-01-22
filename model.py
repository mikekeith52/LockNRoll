import random
import numpy as np
import pandas as pd
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from itertools import product

import game
from ActionHash import ActionHash
from config import GAMMA, LEARNING_RATE, MEMORY_SIZE, BATCH_SIZE, EXPLORATION_MAX, EXPLORATION_MIN, EXPLORATION_DECAY

def evaluate_reward(game_state,action):
    init_points = game_state.points
    init_jokers = game_state.jokers
    choice = ActionHash().get(action)

    if choice[0] == 'JO':
        game_state.place_joker(choice[1] + 1)
    else:
        game_state.place_die(choice[0],choice[1] + 1)
    game_state.lock_n_roll()

    if game_state.gameover:
        return -10
    else:
        return (game_state.points - init_points)

class AVActions:
    def __init__(self,game_state):
        self.game_state = game_state
        expand_grid = lambda d: pd.DataFrame([row for row in product(*d.values())],columns=d.keys())
        actions = expand_grid({'DIE':game_state.dice,'AVSPACE':[i for i,v in enumerate(game_state.board) if v.isnumeric()]})
        if game_state.jokers > 0:
            actions = actions.append(expand_grid({'DIE':['JO'],
                'AVSPACE':[i for i,v in enumerate(game_state.board) if i not in game_state.joker_on_board]}),
                ignore_index=True,sort=False)

        actions = actions.set_index(['DIE','AVSPACE']).sort_index()
        self.available = actions.index
        state = {}
        for i,v in enumerate(game_state.board):
            state[f'BOARD_IDX_{i}_JO'] = 0
            for c in 'YGBR':
                state[f'BOARD_IDX_{i}_C{c}'] = 0
            if (not v.isnumeric()) & (not v == 'JO'):
                state[f'BOARD_IDX_{i}_C{v[0]}'] = 1
            for n in '1234':
                state[f'BOARD_IDX_{i}_N{n}'] = 0
            if (not v.isnumeric()) & (not v == 'JO'):
                state[f'BOARD_IDX_{i}_N{v[1]}'] = 1
            if v == 'JO':
                state[f'BOARD_IDX_{i}_JO'] = 1
        self.state = tuple(state.values())

class DQNSolver:
    def __init__(self, action_space, observation_space, memory = None, model = None, exploration_rate = None):
        self.exploration_rate = EXPLORATION_MAX if exploration_rate is None else exploration_rate
        self.action_space = action_space
        self.actionhash = ActionHash()
        self.memory = deque(maxlen=MEMORY_SIZE) if memory is None else memory
        if model is None:
            self.model = Sequential()
            self.model.add(Dense(500, input_shape=(observation_space,), activation="relu"))
            self.model.add(Dense(500, activation="relu"))
            self.model.add(Dense(self.action_space, activation="linear"))
            self.model.compile(loss="mse", optimizer=Adam(lr=LEARNING_RATE))
        else:
            self.model = model

    # state will be a tuple of 1/0s, action is the chosen action's index, reward is the total points gained from the action, next_state is another tuple of 0/1, done is whether there is a game over
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, game, state):
        available_actions = AVActions(game).available
        if np.random.rand() < self.exploration_rate:
            while True:
                choice = np.random.choice(self.action_space,size=1)[0]
                if self.actionhash.get(choice) in available_actions:
                    return choice
        q_values = self.model.predict(state)
        q_hashed = {} # chaining hash table
        for i, v in enumerate(q_values[0]):
            if v not in q_hashed:
                q_hashed[v] = [i]
            else:
                q_hashed[v].append(i)
        q_sorted = sorted(q_values[0])[::-1] # rate all actions best-to-worst
        for q in q_sorted: # iterate until you find the best available action
            for i in q_hashed[q]:
                if self.actionhash.get(i) in available_actions:
                    return i

    def experience_replay(self, game):
        if len(self.memory) < BATCH_SIZE:
            return
        batch = random.sample(self.memory, BATCH_SIZE)
        for state, action, reward, state_next, terminal in batch:
            q_update = reward
            if not terminal:
                q_update = (reward + GAMMA * np.median(self.model.predict(state_next)[0])) # use mean becasue you don't know the actions available in the next state every time
            q_values = self.model.predict(state)
            q_values[0][action] = q_update
            self.model.fit(state, q_values, verbose=0)
        self.exploration_rate *= EXPLORATION_DECAY
        self.exploration_rate = max(EXPLORATION_MIN, self.exploration_rate)