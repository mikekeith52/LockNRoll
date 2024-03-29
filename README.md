
# WELCOME TO LOCK N' ROLL PYTHON!
*Disclaimer: as far as I am aware, Armor Games owns the Lock N' Roll intellectual property. I am not affiliated with this orgnization in any way. None of the code I developed is from the actual game's source code. The real game ([here](https://armorgames.com/play/4283/lock-n-roll#:~:text=Lock%20'n'%20Roll%20is%20an,according%20to%20number%20and%20color)) is much more fun and I'd encourage you to play it instead of this.*

Check out the corresponding Towards Data Science article: [Reinforcement Learning Lock N' Roll](https://towardsdatascience.com/reinforcement-learning-lock-n-roll-eec6719dfe1)

## AI
- An AI is being trained to master this game, see [AI.MD](https://github.com/mikekeith52/LockNRoll/blob/main/AI.MD) or the aforementioned Towards Data Science article for an overview of that process
- This readme is an overview of Lock N' Roll the game and how to play it using the Python application

## Rules
![](https://i2.wp.com/cannedbanana.files.wordpress.com/2009/01/lnr-rules.jpg)

In addition to the rules explained in this figure, a common rule for Lock N' Roll applications is to treat any board clear as an automatic earned joker, which means a joker bonus if two jokers have already been obtained. This additional rule is incorporated in this application.

## Python Rendering
- The colors yellow, red, blue, and green are rendered as Y, R, B, G respectively
- The numbers are 1, 2, 3, 4
  - Example: the yellow 1 die is represented as Y1
- Joker is rendered as JO when placed on the board
- The board positions are labeled 1 - 16 left-to-right, up-to-down
- Like this:
```python
"""
		==================
		||01||02||03||04||
		==================
		||05||06||07||08||
		==================
		||09||10||11||12||
		==================
		||13||14||15||16||
		==================
"""
```

## How to Play
- Uses a command-line interface:
	- `cd path/to/directory`
	- `pip install -r requirements.txt`
	- `python app.py`
1. To place a die, type 1 followed by a **space** followed by the die you want to place (ex: R4) followed by a comma, followed by the position you want to place it (no need for the leading zero)
	  - Example: typing: "1 R4,1" (no quotes) or "1 r4,1" will place the R4 die on position 1, if you have an R4 die and if position 1 is available
	  - Your board will then be rendered as:
```python
"""
		==================
		||R4||02||03||04||
		==================
		||05||06||07||08||
		==================
		||09||10||11||12||
		==================
		||13||14||15||16||
		==================
"""
```
2. To place a joker, type 2 followed by a **space** followed by the position you want to place the joker
    - If a space is already covered by a die, you can still place a joker there by using the space's position as if there were no die there
    - Example: typing "2 6" will place a joker on position 6, whether or not that space has already been played, if you have a joker available
    - Your board will be rendered as
```python
"""
		==================
		||R4||02||03||04||
		==================
		||05||JO||07||08||
		==================
		||09||10||11||12||
		==================
		||13||14||15||16||
		==================
"""
```
3. To score the board, clear any spaces based on combinations of dice you have placed on the board, and get new dice if you are out, type 3
4. If you want to print an empty board, type 4 (this is useful to reference when trying to place a joker)
5. To let the AI play a move, type 5
6. To exit, type 6 

**Note, there is no way to reverse a move, so be careful**