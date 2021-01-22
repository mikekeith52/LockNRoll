import game
import pickle
import numpy as np
import os
from ActionHash import ActionHash
from model import evaluate_reward, AVActions, DQNSolver
from keras.models import load_model
from config import EXPLORATION_MAX, previous_model

def train():
    g = game.Game(quiet=True)
    action_space = ActionHash().__len__()
    observation_space = len(AVActions(g).state)
    memory = pickle.load(open('model/memory.pckl','rb')) if previous_model else None
    model = load_model('model/model.h5') if previous_model else None
    total_moves, run, exploration_rate = pickle.load(open('model/misc.pckl','rb')) if previous_model else (0,0,EXPLORATION_MAX)
    dqn_solver = DQNSolver(action_space, observation_space, memory, model, exploration_rate)
    while True:
        run += 1
        g = game.Game(quiet=True)
        state = AVActions(g).state
        state = np.reshape(state, [1, observation_space])
        while not g.gameover:
            total_moves += 1
            action = dqn_solver.act(g, state)
            reward = evaluate_reward(g,action)
            terminal = g.gameover
            state_next = AVActions(g).state
            state_next = np.reshape(state_next, [1, observation_space])
            dqn_solver.remember(state, action, reward, state_next, terminal)
            state = state_next
            if terminal:
                # ADD LOGGING
                print("Game: " + str(run) + ", exploration: " + str(dqn_solver.exploration_rate) + ", score: " + str(g.points) + ", moves: " + str(g.moves) + ", total moves: " + str(total_moves))
                mode = 'a' if (os.path.exists('log.csv')) & (run > 1) else 'w'
                with open('log.csv',mode) as log:
                    log.write(f'{run},{dqn_solver.exploration_rate},{g.points},{g.moves}\n')
                # overwrite most current model iteration
                with open('model/memory.pckl','wb') as pckl:
                    pickle.dump(dqn_solver.memory,pckl)
                with open('model/misc.pckl','wb') as pckl:
                    misc = (total_moves, run, exploration_rate)
                    pickle.dump(misc,pckl)
                dqn_solver.model.save('model/model.h5')
            else:
                dqn_solver.experience_replay(g)

if __name__ == "__main__":
    train()