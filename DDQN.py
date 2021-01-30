import random
import numpy as np
import os
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import RMSprop as OPTIMIZER

import game
from config import GAMMA, LEARNING_RATE, MEMORY_SIZE, BATCH_SIZE, EXPLORATION_MAX, EXPLORATION_MIN, EXPLORATION_DECAY, REPLAY_START_SIZE, TRAINING_FREQUENCY

class DDQNTrainer:
    def __init__(self, action_space, observation_space, memory = None, model = None, exploration_rate = None):
        self.action_space = action_space
        self.epsilon = EXPLORATION_MAX if exploration_rate is None else exploration_rate
        self.memory = [] if memory is None else memory
        if model is None:
            self.model = Sequential()
            self.model.add(Dense(observation_space*4, input_shape=(observation_space,), activation="relu"))
            self.model.add(Dense(observation_space*4, activation="relu"))
            self.model.add(Dense(self.action_space, activation="linear"))
            self.model.compile(loss="mean_squared_error",
                                optimizer=OPTIMIZER(lr=LEARNING_RATE,
                                                     rho=GAMMA,
                                                     epsilon=EXPLORATION_MIN),
                                metrics=["accuracy"])
        else:
            self.model = model

    # state will be a tuple of 1/0s, action is the chosen action's index, reward is the total points gained from the action, next_state is another tuple of 0/1, done is whether there is a game over
    def remember(self, current_state, action, reward, next_state, terminal):
        self.memory.append({"current_state": current_state,
                            "action": action,
                            "reward": reward,
                            "next_state": next_state,
                            "terminal": terminal})
        if len(self.memory) > MEMORY_SIZE:
            self.memory.pop(0)

    def step_update(self, total_step):
        if len(self.memory) < REPLAY_START_SIZE:
            return

        if total_step % TRAINING_FREQUENCY == 0:
            loss, accuracy, average_max_q = self._train()
            mode = 'a' if os.path.exists('log.log') & (total_step > TRAINING_FREQUENCY) else 'w'
            with open('log.log',mode) as f:
                f.write(f'moves: {total_step}, loss: {loss}, accuracy: {accuracy}, average_max_q: {average_max_q}\n')

        self._update_epsilon()

    def act(self, current_state):
        if (np.random.rand() < self.epsilon) | (len(self.memory) < REPLAY_START_SIZE):
            return random.randrange(self.action_space)
        q_values = self.model.predict(current_state)
        return np.argmax(q_values[0])

    def evaluate_reward(self,game,action):
        init_points = game.points
        if ((len(game.dice) > 0) & (len([i for i in game.board if i.isnumeric()]) > 0)) | (game.jokers > 0):
            if game.board[action].isnumeric():
                next_die = game.dice[0]
                game.place_die(next_die,action+1)
            elif len([i for i in game.board if i.isnumeric()]) > 0:
                next_die = game.dice[0]
                adjusted_pos = min([int(i) for i in game.board if i.isnumeric()],key = lambda x: abs(x-(action+1)))
                game.place_die(next_die,adjusted_pos)
            elif (game.jokers > 0) & (action not in game.joker_on_board):
                game.place_joker(action+1)
            else:
                adjusted_pos = min([int(i) for i,v in enumerate(game.board) if i not in game.joker_on_board],key = lambda x: abs(x-action))
                game.place_joker(adjusted_pos+1)
                
        game.lock_n_roll()
        if game.gameover:
            return game.points - init_points - 500
        else:
            return game.points - init_points

    def _train(self):
        batch = np.asarray(random.sample(self.memory, BATCH_SIZE))
        if len(batch) < BATCH_SIZE:
            return

        current_states = []
        q_values = []
        max_q_values = []

        for entry in batch:
            current_state = entry["current_state"]
            current_states.append(current_state)
            next_state = entry["next_state"]
            next_state_prediction = self.model.predict(next_state)[0]
            next_q_value = np.max(next_state_prediction)
            q = list(self.model.predict(current_state)[0])
            if entry["terminal"]:
                q[entry["action"]] = entry["reward"]
            else:
                q[entry["action"]] = entry["reward"] + GAMMA * next_q_value
            q_values.append(q)
            max_q_values.append(np.max(q))

        fit = self.model.fit(np.asarray(current_states).squeeze(),
                            np.asarray(q_values).squeeze(),
                            batch_size=BATCH_SIZE,
                            verbose=0)
        loss = fit.history["loss"][0]
        accuracy = fit.history["accuracy"][0]
        return loss, accuracy, np.mean(max_q_values)

    def _update_epsilon(self):
        self.epsilon -= EXPLORATION_DECAY
        self.epsilon = max(EXPLORATION_MIN, self.epsilon)