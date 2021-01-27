import pandas as pd
import numpy as np
import random
from sklearn.decomposition import PCA
import pickle
import game
from State import State
import numpy as np



if __name__ == '__main__':
    g = game.Game()
    state = State(g)
    state_r = StateReduced(state)
    print(state_r.state)