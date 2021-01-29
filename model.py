from keras.models import Sequential
from keras.layers import Conv2D, Flatten, Dense
from keras.optimizers import RMSprop as OPTIMIZER

class DDQN_MODEL:
	def __init__(self, action_space, observation_space):
		    self.model = Sequential()
            self.model.add(Dense(observation_space*4, input_shape=(observation_space,), activation="relu"))
            self.model.add(Dense(observation_space*4, activation="relu"))
            self.model.add(Dense(self.action_space, activation="linear"))
            self.model.compile(loss="mean_squared_error",
                               optimizer=OPTIMIZER(lr=LEARNING_RATE,
                                                 rho=GAMMA,
                                                 epsilon=EXPLORATION_MIN),
                               metrics=["accuracy"])