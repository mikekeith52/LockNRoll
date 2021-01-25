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
            return spaces_cleared*100 # since we already awarded it for getting good combos

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
        self.available = list(actions.index.unique())
        self.available.append(('LO','RO'))
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
        
        # which dice are available to play
        for c in 'YGBR':
            for n in '1234':
                state[f'DICE_AV_{c+n}'] = 0
        for d in game_state.dice:
            state[f'DICE_AV_{d}'] = 1

        state['LASTMOVELOCKROLL'] = int(game_state.last_move_lock_n_roll)
        state['JOKERS'] = game_state.jokers
        state['POINTSTONEXTJOKER'] = game_state.next_joker
        state['NEXTJOKERBONUS'] = game_state.next_joker_bonus
        
        self.state = tuple(state.values())
        self.labels = tuple(state.keys())

class DQNSolver:
    def __init__(self, action_space, observation_space, memory = None, model = None, exploration_rate = None):
        self.exploration_rate = EXPLORATION_MAX if exploration_rate is None else exploration_rate
        self.action_space = action_space
        self.actionhash = ActionHash()
        self.memory = deque(maxlen=MEMORY_SIZE) if memory is None else memory
        if model is None:
            self.model = Sequential()
            self.model.add(Dense(492, input_shape=(observation_space,), activation="relu"))
            self.model.add(Dense(492, activation="relu"))
            self.model.add(Dense(self.action_space, activation="linear"))
            self.model.compile(loss="mse", optimizer=OPTIMIZER(lr=LEARNING_RATE))
        else:
            self.model = model

    # state will be a tuple of 1/0s, action is the chosen action's index, reward is the total points gained from the action, next_state is another tuple of 0/1, done is whether there is a game over
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, game, state):
        available_actions = AVActions(game).available
        if np.random.rand() < self.exploration_rate:
            choice = np.random.choice(self.action_space,size=1)[0]
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