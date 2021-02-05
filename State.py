import game
import pickle
import numpy as np
from sklearn.preprocessing import OneHotEncoder

PCA_MODEL = pickle.load(open('model/pca.pckl','rb'))
LDA_MODEL = pickle.load(open('model/lda.pckl','rb'))
ReducedObsSpacePCA = PCA_MODEL.n_components_
ReducedObsSpaceLDA = len(LDA_MODEL.explained_variance_ratio_)

class State:
    def __init__(self,game_state):
        game_state.dice = sorted(game_state.dice) # to reduce the total number of possible states
        self.state_dict = {'JokerAv':game_state.jokers}
        for t in range(4):
            for c in 'BGRY':
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
            if len([v for v in game_state.board if v.isnumeric()]) > 0:
                self.state_dict[f'Move_{i}_Dist'] = min([i for i,v in enumerate(game_state.board) if v.isnumeric()], key = lambda x:abs(x-i)) - i
            else: 
                self.state_dict[f'Move_{i}_Dist'] = 0

        for i,v in enumerate(game_state.board):
            if (not v.isnumeric()) & (v != 'JO'):
                self.state_dict[f'Space{i}_CoveredByC_{v[0]}'] = 1
                self.state_dict[f'Space{i}_CoveredByN_{v[1]}'] = 1
            elif v == 'JO':
                self.state_dict[f'Space{i}_CoveredByJO'] = 1
        
        self.state = tuple(self.state_dict.values())
        self.labels = tuple(self.state_dict.keys())
        self.reshaped_state = np.reshape(self.state, [1, len(self.state)])
        self.reduced_state_pca = PCA_MODEL.transform(self.reshaped_state)
        self.reduced_state_lda = LDA_MODEL.transform(self.reshaped_state)

if __name__ == '__main__':
    g = game.Game()
    state = State(g)
    print(len(state.state))
    for k, v in state.state_dict.items():
        print(k,v)

    state_r = state.reduced_state_pca
    print('Reduced State PCA:',state_r)

    state_r = state.reduced_state_lda
    print('Reduced State LDA:',state_r)