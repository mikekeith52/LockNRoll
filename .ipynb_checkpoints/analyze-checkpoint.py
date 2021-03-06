import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

order = 2
column = 'Score'

def main():
	df = pd.read_csv('log.csv',names=['Game','ExplrRt','Score','Moves'])

	if df.shape[0] < (order + 2):
		print('Need more observations before plotting')
		return

	ax = sns.lineplot(x='Game',y=column,data=df)
	ax.axvline(df.loc[df['ExplrRt'] < 1,'Game'].min(), color="red", linestyle="--")
	sns.regplot(x='Game',y=column,data=df,order=order)
	plt.show()

if __name__ == '__main__':
	main()
