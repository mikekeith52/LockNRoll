import game

class State:
    def __init__(self,game_state):
        game_state.dice = sorted(game_state.dice) # to reduce the total number of possible states
        self.state_dict = {'JokerAv':game_state.jokers}
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