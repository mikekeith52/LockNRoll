import numpy as np
from model import Actions
from ActionHash import ActionHash
from keras.models import load_model
import matplotlib.pyplot as plt
import seaborn as sns

import game

def get_state(g):
	for s,l in zip(Actions(g).state,Actions(g).labels):
		print(s,l)

def see_pred(g):
	action_space = ActionHash().__len__()
	observation_space = len(Actions(g).state)
	model = load_model('model/model.h5')
	state = Actions(g).state
	state = np.reshape(state, [1, observation_space])
	q_values = model.predict(state)

	for x1,x2 in zip(ActionHash().table,q_values[0]):
		print(x1,x2)

if __name__ == '__main__':
	g = game.Game(quiet=True)
	get_state(g)
	see_pred(g)