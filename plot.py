import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

order = 2
column = 'Reward'

def main():
	df = pd.read_csv('log.csv',names=['Game','ExplrRt','Score','Reward','Moves'])
	df['RewardPerGameMove'] = df['Reward']/df['Moves']

	sns.lineplot(x='Game',y=column,data=df)
	sns.regplot(x='Game',y=column,data=df,order=order)
	plt.show()

if __name__ == '__main__':
	main()
