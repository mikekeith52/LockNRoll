import numpy as np
from State import State, StateReducedLDA, ReducedObsSpaceLDA
from keras.models import load_model
import matplotlib.pyplot as plt
import seaborn as sns

import game

def get_state(g):
	print(len(State(g).labels))
	for l,s in State(g).state_dict.items():
		print(s,l)

def see_pred(g):
	action_space = 16
	observation_space = ReducedObsSpaceLDA
	model = load_model('model/model.h5')
	state = StateReducedLDA(State(g)).state
	state = np.reshape(state, [1, observation_space])
	q_values = model.predict(state)

	for x1,x2 in enumerate(q_values[0]):
		print(x1,x2)

if __name__ == '__main__':
	g = game.Game(quiet=True)
	get_state(g)
	see_pred(g)