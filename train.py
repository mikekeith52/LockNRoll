import game
import pickle
import numpy as np
import os
from State import State, ReducedObsSpaceLDA
from DDQN import DDQNTrainer
from keras.models import load_model
from config import EXPLORATION_MAX, MAX_ITERS, REPLAY_START_SIZE, continue_last_model 

def train():
    g = game.Game(quiet=True)
    action_space = 16
    observation_space = ReducedObsSpaceLDA
    memory = pickle.load(open('model/memory.pckl','rb')) if continue_last_model else None
    model = load_model('model/model.h5') if continue_last_model else None
    total_moves, run, exploration_rate = pickle.load(open('model/misc.pckl','rb')) if continue_last_model else (0,0,EXPLORATION_MAX)
    ddqn_trainer = DDQNTrainer(action_space, observation_space, memory, model, exploration_rate)
    while total_moves < MAX_ITERS:
        run += 1
        g = game.Game(quiet=True)
        current_state = State(g).reduced_state_lda
        while not g.gameover:
            action = ddqn_trainer.act(current_state)
            total_moves+=1
            reward = ddqn_trainer.evaluate_reward(g,action)
            print(f'move: {action}, reward: {reward}')
            next_state = State(g).reduced_state_lda
            ddqn_trainer.remember(current_state, action, reward, next_state, g.gameover)
            current_state = next_state
            ddqn_trainer.step_update(total_moves)
            # state log - for monitoring
            if total_moves > REPLAY_START_SIZE:
                with open('state.log','w') as log:
                    for k,v in State(g).state_dict.items():
                        log.write(f'{k} {v}\n')
            if g.gameover:
                # game log
                print("Game:",str(run),"exploration:",str(ddqn_trainer.epsilon),"score:",str(g.points),"moves:",str(g.moves),"total moves:",str(total_moves))
                mode = 'a' if (os.path.exists('log.csv')) & (run > 1) else 'w'
                with open('log.csv',mode) as log:
                    log.write(f'{run},{ddqn_trainer.epsilon},{g.points},{g.moves}\n')
                # overwrite most current model iteration
                if total_moves > REPLAY_START_SIZE:
                    with open('model/memory.pckl','wb') as pckl:
                        pickle.dump(ddqn_trainer.memory,pckl)
                    with open('model/misc.pckl','wb') as pckl:
                        misc = (total_moves, run, ddqn_trainer.epsilon)
                        pickle.dump(misc,pckl)
                    ddqn_trainer.model.save('model/model.h5')
                
if __name__ == "__main__":
    train()