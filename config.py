GAMMA = 0.95
LEARNING_RATE = 0.00025

MEMORY_SIZE = 1000000 # the maximum capacity to remember
BATCH_SIZE = 32

EXPLORATION_MAX = 1.0
EXPLORATION_MIN = 0.005
EXPLORATION_STEPS = 250000
EXPLORATION_DECAY = (EXPLORATION_MAX-EXPLORATION_MIN)/EXPLORATION_STEPS
REPLAY_START_SIZE = 50000
TRAINING_FREQUENCY = 4

TARGET_NETWORK_UPDATE_FREQUENCY = 40000
MODEL_PERSISTENCE_UPDATE_FREQUENCY = 10000

MAX_ITERS = 5000000

continue_last_model = True