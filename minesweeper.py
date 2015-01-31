# Minesweeper that you can play in terminal!

# Future improvements:
# display how many mines are left? 
# GUI  (Tkinter? pygame?)

# Written by Carolyn Ranti
# 1/31/2015

from random import shuffle
from sys import stdin, stdout
from time import time

####
#Constants to set the status/symbol of a BoardSpace:
UNTOUCHED = 1
TRIPPED = 2 #spot tripped, either by selecting it or by 
FLAGGED = 3 #this marks the spot as a "maybe"
MARKED = 4 #this marks it as a mine (protection, somewhat) 
SYMBOL = {UNTOUCHED:"[ ]", 
		TRIPPED:{"mine":' X ', "empty": ' - '}, 
		FLAGGED: '[?]',
		MARKED:"[*]"}

#Difficulty settings: (nRows, nCols, nMines)
DIFFICULTY = {'e': (9,9,10), 
			'm':(16,16,40), 
			'h':(16,30,99)}

instructions = """
***************** Welcome to Carolyn's Minesweeper! *****************

The goal in this game is to find all of the mines in a board.
 
To select a move in each turn, type 3 characters, separated by commas:
	1.  A letter: T, M, or F
		> T - trip a space on the board. If there is a mine 
		  there, you lose the game. Otherwise, you will see 
		  how many mines border that space.
		> M - mark a space as a mine. This provides some 
		  protection - if you try to trip a marked space, 
		  you'll be asked for confirmation. Also, you can 
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

There are several levels of difficulty to choose from:
	Easy (9x9 board, 10 mines)
	Medium (16x16 board, 40 mines)
	Difficult (16x30 board, 99 mines)
	Custom (user-entered. Maximum 50 rows or columns)

Type "forfeit" at any point to end a game.

Let's begin!
**********************************************************************
"""

class BoardSpace(object):
	def __init__(self,r,c,mine=False):
		self.location = (r,c) #location of the space in a board
		self.neighbors = {}
		self.mine = mine #Boolean: does this space have a mine?
		self._numAdjMines = None

		#space status (UNTOUCHED, tripped, FLAGGED, or marked)
		self.status = UNTOUCHED; 
		return

	@property
	def numAdjMines(self):
		''' 
		Only does the calculation the first time it's called 
		'''
		if self._numAdjMines == None:
			nMines = len([n for n in self.neighbors.values() if n.mine])
			self._numAdjMines = nMines
		return self._numAdjMines

	def tripNeighbors(self):
		''' 
		If a space with 0 adjacent mines is tripped,
		it also trips all its neighbors (which trip their 
		neighbors in turn, if they also have 0 adj. mines...)
		'''	
		spacesTripped = 0
		if self.numAdjMines==0:
			for n in self.neighbors.values():
				if not n.status == TRIPPED:
					n.trip()
					spacesTripped +=1
					spacesTripped += n.tripNeighbors()
		return spacesTripped

	def trip(self):
		if not self.status == TRIPPED:
			self.status = TRIPPED
		return

	def flag(self):
		if not self.status == TRIPPED:
			#toggle status w/ UNTOUCHED
			if self.status == FLAGGED:
				self.status = UNTOUCHED

			self.status = FLAGGED
		return

	def mark(self):
		if not self.status == TRIPPED:
			#toggle status w/ UNTOUCHED
			if self.status == MARKED:
				self.status = UNTOUCHED

			self.status = MARKED
		return

class MSGame(object):
	def __init__(self,nRows,nCols,nMines):
		
		#these are all set by startNewGame
		self.board = None #list of lists with BoardSpaces
		self.minePairs = None #list of all the mines in board (randomly placed)
		self.gameStatus = False #boolean indicating if the game is ongoing

		self.startNewGame(nRows, nCols, nMines)

		self.numTripped = 0
		self.winStatus = False #True if user wins.
		return

	@property
	def nRows(self):
		if self.board:
			return len(self.board)
		else:
			return 0

	@property
	def nCols(self):
		if self.board:
			return len(self.board[0])
		else:
			return 0

	@property
	def nMines(self):
		if self.minePairs:
			return len(self.minePairs)
		else:
			return 0

	@property
	def numSafeToTrip(self):
		return self.nRows*self.nCols - self.nMines


	def startNewGame(self,nRows,nCols,nMines):
		''' Create a new board with input specs. 
		Set board, mineCoords, and gameStatus'''
		self.minePairs = self.createBoard(nRows,nCols,nMines) 
		self.gameStatus = True
		return

	def createBoard(self,nRows=9,nCols=9,nMines=10):
		''' 
		Create a [nRows] by [nCols] minesweeper board (a nested array
		with BoardSpaces), and place [nMines] mines randomly on the board
			Standard difficulties
			- Easy: 9x9 board, 10 mines (default)
			- Int: 16x16 board, 40 mines
			- Hard: 16x30 board, 99 mines
		'''
		board = [[] for i in range(nRows)]
		for r in xrange(nRows):
			for c in xrange(nCols):
				board[r].append(BoardSpace(r,c))

		# set all neighbor references once the board has been filled
		for r in xrange(nRows):
			for c in xrange(nCols):
				if c > 0:
					board[r][c].neighbors['N'] = board[r][c-1]
					if r < nRows-1:
						board[r][c].neighbors['NE'] = board[r+1][c-1]
					if r > 0:
						board[r][c].neighbors['NW'] = board[r-1][c-1]
				if r < nRows-1:
					board[r][c].neighbors['E'] = board[r+1][c]
				if c < nCols-1:
					board[r][c].neighbors['S'] = board[r][c+1]
					if r < nRows-1:
						board[r][c].neighbors['SE'] = board[r+1][c+1]
					if r > 0:
						board[r][c].neighbors['SW'] = board[r-1][c+1]
				if r > 0:
					board[r][c].neighbors['W'] = board[r-1][c]

		# place nMines randomly
		mineSpots=range(nRows*nCols)
		shuffle(mineSpots)
		mineSpots=mineSpots[:nMines]
		minePairs = []
		for mS in mineSpots:
			r = mS % nRows
			c = mS / nRows
			minePairs.append((r,c))
			# print r,c #for debugging only!
			board[r][c].mine=True 

		self.board = board
		return minePairs

	def tripSpace(self,r,c):
		''' - If user trips a mine, they lose the game.
			- Call tripNeighbors() -- will only do something if the space has 0 mines
			- Increment the number of tripped squares.
			- Tripping a square cannot be undone.
			- Check if the user WON the game by tripping the square '''
		space = self.board[r][c]
		
		if space.mine:
			self.endGame(False)
		else:
			space.trip()
			#try to trip all neighbors
			nTripped = space.tripNeighbors()
			self.numTripped += 1 + nTripped
			self.checkWinStatus() #check if you won with that square
		return

	def flagSpace(self,r,c): 
	 	'''Reverses the flag status of board[r][c], as long as it hasn't been tripped'''
		self.board[r][c].flag()
		return

	def markSpace(self,r,c): 
		'''Reverses the mark status of board[r][c], as long as it hasn't been tripped
		Check if you won by flagging that square (i.e. if it is the last mine to flag.) '''
		self.board[r][c].mark()
		self.checkWinStatus() #check if you won by flagging that square
		return

	def checkWinStatus(self):
		''' Checks if the number of tripped squares equals the number
		of squares that are "safe" to trip (i.e. non mines)
		If those numbers are not equal, it checks to see if all mines
		have been marked (the other way to win the game) '''
		if self.numSafeToTrip == self.numTripped:
			self.endGame(True) #win the game
			return

		#check all mines, exiting this function if any aren't marked
		for (r,c) in self.minePairs:
			if not self.board[r][c].status == MARKED:
				return

		self.endGame(True)
		return

	def endGame(self,winStatus):
		""" 
		Set game status to False to end the game, and trip all the 
		spaces, so that board can be printed in its entirety.
	    NOTE: Not tripping squares (correctly) marked squares as mines, 
	    so the user can see what they did correctly. 
	    """

		for r in self.board:
			for c in r:
				if not (c.mine == True and c.status == MARKED):
					c.trip()

		self.gameStatus = False
		self.winStatus = winStatus
		return

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
		# if the space is currently marked, verify with the user that they want to 
		# trip it (marking a spot therefore provides a little protection from mistakes)
		# TODO - make this check better?
		if currSpaceStatus  == MARKED:
		 	stdout.write('Are you sure? This spot is currently marked as a potential mine. (Y/N): ')
		 	ans = stdin.readline().strip().lower()
		 	if ans=='n':
		 		return False
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

	#print board, ask for a move, repeat until gameStatus is false
	while G.gameStatus:
		boardPrint(G.board) #print out board
		stdout.write('Select a move ([t/f/m],row,col): ')
		userInput = stdin.readline().strip()
		moveSuccess = playMove(G,userInput)
		if not moveSuccess:
			print 'Try entering that move again.'
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

