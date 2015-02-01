# Play minesweeper in terminal
#
#
# Future updates: 
#   - display how many mines are left? 

# Carolyn Ranti
# 2/1/2015

from minesweeper import *

SYMBOL = {UNTOUCHED:"[ ]", 
		TRIPPED:{"mine":' X ', "empty": ' - '}, 
		FLAGGED: '[?]',
		MARKED:"[*]"}

instructions = """
***************** Welcome to Carolyn's Minesweeper! *****************

The goal in this game is to find all of the mines in a board.
 
To select a move in each turn, type 3 characters, separated by commas:
	1.  A letter: T, M, or F
		> T - trip a space on the board. If there is a mine 
		  there, you lose the game. Otherwise, you will see 
		  how many mines border that space.
		> M - mark a space as a mine. This protects the space -  
		  you cannot trip a marked space. In addition, you can 
		  win the game by marking all of the mines in a board
		  (even if there are untripped spaces).
		> F - flag the space as a potential mine. This is 
		  just for you to keep track of things.

	2.  An integer, to select a row of the board

	3.  An integer, to select a column of the board

	For example, to trip the square in row 3, column 2, enter:
		T,3,2

	Or to flag the square in row 10, column 4, enter:
		F,10,4

	Letters are not case-sensitive (e.g. f,10,4 is fine)

On the board, you will see the following kinds of symbols:
	[ ] is an untripped square
	[1] is a tripped square with 1 mine bordering it
	 -  is a tripped square with no mines bordering it
	[*] is a marked square
	[?] is a flagged square
	 X  is a mine

After each move, you will be told how many mines are left. This is based solely on the NUMBER of marked spaces -- it does not reveal whether the marked spaces are truly mines.

There are several levels of difficulty to choose from:
	Easy (9x9 board, 10 mines)
	Medium (16x16 board, 40 mines)
	Difficult (16x30 board, 99 mines)
	Custom (user-entered. Maximum 50 rows or columns)

Type "forfeit" at any point to end a game.

Let's begin!
**********************************************************************
"""


''' Convert a board's status to a symbol to print in terminal ''' 
def symbol(space):
	if space.status == TRIPPED:
		if space.mine:
			return SYMBOL[TRIPPED]["mine"]
		elif space.numAdjMines > 0:
			return '[%d]' % space.numAdjMines
		else:
			return SYMBOL[TRIPPED]["empty"]
	else:
		return SYMBOL[space.status]


#TODO - edit this to use better print formatting
def boardPrint(board):
	# print row and column numbers
	rowLen = len(board)
	colLen = len(board[0])
	print 'R\\C',
	print ''.join("{:^3}".format(str(c+1)) for c in xrange(colLen))
	for row in xrange(rowLen):
		#column number (centered in 4 char space)
		colNum = "{:^3}".format(str(row+1))
		entireRow = ''.join([symbol(sp) for sp in board[row]])
		print colNum + ' ' + entireRow
	return

def playMove(game, uInput):
	''' Play a move entered by the user (uInput)
	Return a boolean indicating whether the move was valid
	''' 

	if uInput.lower() == "forfeit":
		game.endGame(False) # forfeit the game
		return True

	ui = uInput.split(',')
	if not len(ui) == 3:
		print 'Must enter 3 chars, separated by commas.'
		return False

	try:
		row = int(ui[1])-1
		col = int(ui[2])-1
	except:
		print 'The 2nd and 3rd chars must be integers.'
		return False

	if row > game.nRows or col > game.nCols:
		print "That space is out of bounds."
		return False

	currSpaceStatus = game.board[row][col].status
	if currSpaceStatus == TRIPPED:
		print 'Nothin to do - this space has been tripped.'
		return False

	if ui[0].lower()=='t':
		# trip the space (although it won't do anything if the space is marked)
		if currSpaceStatus == MARKED:
			print "Can't trip this space - it's currently marked"
		game.tripSpace(row,col)
		return True

	elif ui[0].lower() == 'f':
		game.flagSpace(row,col)
		return True

	elif ui[0].lower() == 'm':
		game.markSpace(row,col)
		return True

	return False

def main():
	#ask the user what level (easy, medium, hard, custom)
	stdout.write('Select a level of difficulty (E=easy, M=medium, H=hard, or C=custom): ')
	l = stdin.readline().strip().lower()
	
	if l=='e' or l=='m' or l=='h':
		(nRows, nCols, nMines) = DIFFICULTY[l]
	else:
		print "Select custom settings: "
		try:
			stdout.write('# rows: ')
			nRows = int(stdin.readline().strip())
			stdout.write('# columns: ')
			nCols = int(stdin.readline().strip())
			stdout.write('# mines: ')
			nMines = int(stdin.readline().strip())
		except:
			print "Invalid entry."
			return

		if nRows > 50:
			print "** Setting # rows to the maximum (50)"
			nRows = 50
		if nCols > 50: 
			print "** Setting # columns to the maximum (50)"
			nCols = 50

		if nMines >= nRows*nCols:
			print "You're crazy! You can't fill the field with mines." 
			return
		elif nMines == 0:
			print 'Oh come on, challenge yourself. You have to put at least ONE mine in there.'
			return

	#start the game!
	startTime = time()
	G = MSGame(nRows, nCols, nMines) 

	print "There are %i mines in the board. Good luck!" % nMines

	#print board, ask for a move, repeat until gameStatus is false
	while G.gameStatus:
		boardPrint(G.board) #print out board
		stdout.write('Select a move ([t/f/m],row,col): ')
		userInput = stdin.readline().strip()
		moveSuccess = playMove(G,userInput)
		# if not moveSuccess:
		# 	print 'Try entering that move again.'
		print "Remaining mines: %i" % (nMines - G.numMarkedSpaces)
	gameTime = time() - startTime

	# Print board and let the user know whether they won or lost
	# (note: when game is ended, all squares are tripped, so the board is printed in its entirety)
	boardPrint(G.board) 
	if G.winStatus:
		print "You win!",
	else:
		print "You lose :-(",

	print "Game time %s:%s" % (str(int(gameTime/60)), str(int(gameTime % 60)).zfill(2))
	
	return

if __name__ == '__main__':
	print instructions

	q = True
	while q:
		main()
		stdout.write('Would you like to play again? (Y/N)')
		ans = stdin.readline().strip()
		if not (ans == 'y' or ans == 'Y'):
			q = False