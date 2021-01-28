import game
import pickle
import numpy as np
import os
from State import State, StateReducedLDA, ReducedObsSpaceLDA
from model import DQNSolver
from keras.models import load_model
from config import EXPLORATION_MAX, MAX_ITERS, continue_last_model

def train():
    g = game.Game(quiet=True)
    action_space = 16
    observation_space = ReducedObsSpaceLDA
    memory = pickle.load(open('model/memory.pckl','rb')) if continue_last_model else None
    model = load_model('model/model.h5') if continue_last_model else None
    total_moves, run, exploration_rate = pickle.load(open('model/misc.pckl','rb')) if continue_last_model else (0,0,EXPLORATION_MAX)
    ddqn_solver = DQNSolver(action_space, observation_space, memory, model, exploration_rate)
    while total_moves < MAX_ITERS:
        run += 1
        g = game.Game(quiet=True)
        state = StateReducedLDA(State(g)).state
        state = np.reshape(state, [1, observation_space])
        while not g.gameover:
            action = ddqn_solver.act(g, state)
            total_moves+=1
            reward = ddqn_solver.evaluate_reward(g,action)
            print(f'move: {action}, reward: {reward}')
            state_next = StateReducedLDA(State(g)).state
            state_next = np.reshape(state_next, [1, observation_space])
            ddqn_solver.remember(state, action, reward, state_next, g.gameover)
            state = state_next
            ddqn_solver.step_update(total_moves)
            # state log - for monitoring
            with open('state.log','w') as log:
                for k,v in State(g).state_dict.items():
                    log.write(f'{k} {v}\n')
            if g.gameover:
                # game log
                print("Game:",str(run),"exploration:",str(dqn_solver.exploration_rate),"score:",str(g.points),"moves:",str(g.moves),"total moves:",str(total_moves))
                mode = 'a' if (os.path.exists('log.csv')) & (run > 1) else 'w'
                with open('log.csv',mode) as log:
                    log.write(f'{run},{dqn_solver.exploration_rate},{g.points},{g.moves}\n')
                # overwrite most current model iteration
                with open('model/memory.pckl','wb') as pckl:
                    pickle.dump(dqn_solver.memory,pckl)
                with open('model/misc.pckl','wb') as pckl:
                    misc = (total_moves, run, dqn_solver.exploration_rate)
                    pickle.dump(misc,pckl)
                ddqn_solver.model.save('model/model.h5')
                
if __name__ == "__main__":
    train()