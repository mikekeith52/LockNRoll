import random
import numpy as np
import pandas as pd
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam as OPTIMIZER
from itertools import product

import game
from State import State
from config import GAMMA, LEARNING_RATE, MEMORY_SIZE, BATCH_SIZE, EXPLORATION_MAX, EXPLORATION_MIN, EXPLORATION_DECAY

class DQNSolver:
    def __init__(self, action_space, observation_space, memory = None, model = None, exploration_rate = None):
        self.exploration_rate = EXPLORATION_MAX if exploration_rate is None else exploration_rate
        self.action_space = action_space
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

    def evaluate_reward(self,game,action):
        init_points = game.points
        if ((len(game.dice) > 0) & (len([i for i in game.board if i.isnumeric()]) > 0)) | (game.jokers > 0):
            if game.board[action].isnumeric():
                next_die = game.dice[0]
                game.place_die(next_die,action+1)
                game.lock_n_roll()
            elif (game.jokers > 0) & (action not in game.joker_on_board):
                game.place_joker(action+1)
                game.lock_n_roll()
            elif len([i for i in game.board if i.isnumeric()]) > 0:
                next_die = game.dice[0]
                adjusted_pos = min([int(i) for i in game.board if i.isnumeric()],key = lambda x: abs(x-action))
                game.place_die(next_die,adjusted_pos)
                game.lock_n_roll()
            else:
                adjusted_pos = min([int(i) for i,v in game.board if i not in game.joker_on_board],key = lambda x: abs(x-action))
                game.place_joker(adjusted_pos+1)

        if game.gameover:
            return game.points - init_points - 100
        else:
            return game.points - init_points

    def experience_replay(self):
        if len(self.memory) < BATCH_SIZE:
            return
        batch = random.sample(self.memory, BATCH_SIZE)
        #batch[-1] = self.memory[-1] # to keep the game moving
        for state, action, reward, state_next, gameover in batch:
            q_update = reward
            if not gameover:
                q_update = (reward + GAMMA * np.amax(self.model.predict(state_next)[0])) # use mean becasue you don't know the actions available in the next state every time
            q_values = self.model.predict(state)
            q_values[0][action] = q_update
            self.model.fit(state, q_values, verbose=0)
        self.exploration_rate = max(EXPLORATION_MIN, self.exploration_rate * EXPLORATION_DECAY)