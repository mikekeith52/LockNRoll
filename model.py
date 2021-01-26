import random
import numpy as np
import pandas as pd
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam as OPTIMIZER
from itertools import product

import game
from helper import score_last_move
from ActionHash import ActionHash
from config import GAMMA, LEARNING_RATE, MEMORY_SIZE, BATCH_SIZE, EXPLORATION_MAX, EXPLORATION_MIN, EXPLORATION_DECAY

def evaluate_reward(game_state,action):
    init_points = game_state.points
    init_open_spaces = sum([1 for i in game_state.board if i.isnumeric()])
    choice = ActionHash().get(action)

    if (len(game_state.dice) > 0) & (len([i for i in game_state.board if i.isnumeric]) > 0):
        pos = int(choice.split('_')[1])
        next_die = game_state.dice[0]
        if game_state.board[pos].isnumeric():
            game_state.place_die(next_die,pos+1)
            game_state.lock_n_roll()
        elif (game_state.jokers > 0) & (pos not in game_state.joker_on_board):
            game_state.place_joker(pos+1)
            game_state.lock_n_roll()
        else:
            return -100 # can't move there

    if game_state.gameover:
        return game_state.points - init_points - 100
    else:
        return game_state.points - init_points

class Actions:
    def __init__(self,game_state):
        self.state_dict = {
            #'SpacesOpen':sum([1 for i in game_state.board if i.isnumeric()]),
            #'DiceAv':len(game_state.dice),
            #'RedsAv':sum([1 for i in game_state.dice if i[0] == 'R']),
            #'YellowsAv':sum([1 for i in game_state.dice if i[0] == 'Y']),
            #'BluesAv':sum([1 for i in game_state.dice if i[0] == 'B']),
            #'GreensAv':sum([1 for i in game_state.dice if i[0] == 'G']),
            #'OnesAv':sum([1 for i in game_state.dice if i[1] == '1']),
            #'TwosAv':sum([1 for i in game_state.dice if i[1] == '2']),
            #'ThreesAv':sum([1 for i in game_state.dice if i[1] == '3']),
            #'FoursAv':sum([1 for i in game_state.dice if i[1] == '4']),
            'JokerAv':game_state.jokers#,
            #'CombosOpen':len(game_state.index_not_scored),
            #'RedsOnBoard':sum([1 for i in game_state.board if i[0] == 'R']),
            #'YellowsOnBoard':sum([1 for i in game_state.board if i[0] == 'Y']),
            #'BluesOnBoard':sum([1 for i in game_state.board if i[0] == 'B']),
            #'RedsOnBoard':sum([1 for i in game_state.board if i[0] == 'G']),
            #'OnesOnBoard':sum([1 for i in game_state.board if (not i.isnumeric()) & (i[1] == '1')]),
            #'TwosOnBoard':sum([1 for i in game_state.board if (not i.isnumeric()) & (i[1] == '2')]),
            #'ThreesOnBoard':sum([1 for i in game_state.board if (not i.isnumeric()) & (i[1] == '3')]),
            #'FoursOnBoard':sum([1 for i in game_state.board if (not i.isnumeric()) & (i[1] == '4')]),
            #'JokersOnBoard':len(game_state.joker_on_board)
            #'LastMoveLR': int(game_state.last_move_lock_n_roll) # just because we have to have a way to punish it if it doesn't want to play
        }
        for t in range(4):
            for c in 'RBGY':
                self.state_dict[f'Die{t}_{c}'] = 0
            for n in '1234':
                self.state_dict[f'Die{t}_{n}'] = 0

        for t,dice in enumerate(game_state.dice):
            self.state_dict[f'Die{t}_{dice[0]}'] = 1
            self.state_dict[f'Die{t}_{dice[1]}'] = 1

        for i in range(16):
            for c in 'RBGY':
                self.state_dict[f'Space{i}_CoveredByC_{c}'] = 0
            for n in '1234':
                self.state_dict[f'Space{i}_CoveredByN_{n}'] = 0
            self.state_dict[f'Space{i}_CoveredByJO'] = 0

        for i,v in enumerate(game_state.board):
            if (not v.isnumeric()) & (v != 'JO'):
                self.state_dict[f'Space{i}_CoveredByC_{v[0]}'] = 1
                self.state_dict[f'Space{i}_CoveredByN_{v[1]}'] = 1
            elif v == 'JO':
                self.state_dict[f'Space{i}_CoveredByJO'] = 1
        
        self.state = tuple(self.state_dict.values())
        self.labels = tuple(self.state_dict.keys())

class DQNSolver:
    def __init__(self, action_space, observation_space, memory = None, model = None, exploration_rate = None):
        self.exploration_rate = EXPLORATION_MAX if exploration_rate is None else exploration_rate
        self.action_space = action_space
        self.actionhash = ActionHash()
        self.memory = deque(maxlen=MEMORY_SIZE) if memory is None else memory
        if model is None:
            self.model = Sequential()
            self.model.add(Dense(observation_space*3, input_shape=(observation_space,), activation="relu"))
            self.model.add(Dense(observation_space*3, activation="relu"))
            self.model.add(Dense(self.action_space, activation="linear"))
            self.model.compile(loss="mse", optimizer=OPTIMIZER(lr=LEARNING_RATE))
        else:
            self.model = model

    # state will be a tuple of 1/0s, action is the chosen action's index, reward is the total points gained from the action, next_state is another tuple of 0/1, done is whether there is a game over
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, game, state):
        if np.random.rand() < self.exploration_rate:
            return random.randrange(self.action_space)
        q_values = self.model.predict(state)
        return np.argmax(q_values[0])

    def experience_replay(self, game):
        if len(self.memory) < BATCH_SIZE:
            return
        batch = random.sample(self.memory, BATCH_SIZE)
        for state, action, reward, state_next, gameover in batch:
            q_update = reward
            if not gameover:
                q_update = (reward + GAMMA * np.amax(self.model.predict(state_next)[0])) # use mean becasue you don't know the actions available in the next state every time
            q_values = self.model.predict(state)
            q_values[0][action] = q_update
            self.model.fit(state, q_values, verbose=0)
        self.exploration_rate *= EXPLORATION_DECAY
        self.exploration_rate = max(EXPLORATION_MIN, self.exploration_rate)