import game
import pickle
import numpy as np
import os
from State import State
from model import DQNSolver
from keras.models import load_model
from config import EXPLORATION_MAX, MAX_ITERS, continue_last_model

def train():
    g = game.Game(quiet=True)
    action_space = 16
    observation_space = len(State(g).state)
    memory = pickle.load(open('model/memory.pckl','rb')) if continue_last_model else None
    model = load_model('model/model.h5') if continue_last_model else None
    total_moves, run, exploration_rate = pickle.load(open('model/misc.pckl','rb')) if continue_last_model else (0,0,EXPLORATION_MAX)
    dqn_solver = DQNSolver(action_space, observation_space, memory, model, exploration_rate)
    while total_moves < MAX_ITERS:
        run += 1
        total_reward = 0
        g = game.Game(quiet=True)
        state = State(g).state
        state = np.reshape(state, [1, observation_space])
        while not g.gameover:
            total_moves += 1
            action = dqn_solver.act(g, state)
            reward = dqn_solver.evaluate_reward(g,action)
            total_reward += reward
            print('move:',action,'reward:',reward)
            state_next = State(g).state
            state_next = np.reshape(state_next, [1, observation_space])
            dqn_solver.remember(state, action, reward, state_next, g.gameover)
            state = state_next
            # JUST FOR LOGGING FOR NOW
            with open('state.log','w') as log:
                for k,v in State(g).state_dict.items():
                    log.write(f'{k} {v}\n')
            if g.gameover:
                # ADD LOGGING
                print("Game:",str(run),"exploration:",str(dqn_solver.exploration_rate),"score:",str(g.points),"total reward:",str(total_reward),"moves:",str(g.moves),"total attempted moves:",str(total_moves))
                mode = 'a' if (os.path.exists('log.csv')) & (run > 1) else 'w'
                with open('log.csv',mode) as log:
                    log.write(f'{run},{dqn_solver.exploration_rate},{g.points},{total_reward},{g.moves},{total_moves}\n')
                # overwrite most current model iteration
                with open('model/memory.pckl','wb') as pckl:
                    pickle.dump(dqn_solver.memory,pckl)
                with open('model/misc.pckl','wb') as pckl:
                    misc = (total_moves, run, dqn_solver.exploration_rate)
                    pickle.dump(misc,pckl)
                dqn_solver.model.save('model/model.h5')
            else:
                dqn_solver.experience_replay()

if __name__ == "__main__":
    train()