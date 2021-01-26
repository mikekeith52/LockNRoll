labels = [
	'SpacesAv',
	'DiceAv',
	'RedsAv',
	'YellowsAv',
	'BluesAv',
	'GreensAv',
	'OnesAv',
	'TwosAv',
	'ThreesAv',
	'FoursAv',
	'JokerAv',
	'CombosOpen',
	'RedsOnBoard',
	'YellowsOnBoard',
	'BluesOnBoard',
	'RedsOnBoard',
]

for c in 'RBGY':
	for n in '1234':
		labels.append(f'NextDie{c}{n}')

actions = []
for i in range(16):
	actions.append(f'PlayJokertoSpaceorLR_{i}')
	actions.append(f'PlayNextDietoSpace_{i}')
actions.append('LR')