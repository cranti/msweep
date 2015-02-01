# Minesweeper that you can play in terminal!

# Probably some bugs left, haven't checked everything thoroughly
# Future improvements:
# GUI  (Tkinter? pygame?)

# Carolyn Ranti
# 2/1/2015

from random import shuffle
from sys import stdin, stdout
from time import time

#### Constants ####
#Set the status/symbol of a BoardSpace:
UNTOUCHED = 1
TRIPPED = 2 #spot tripped, either by selecting it or from neighboring spot with 0 surrounding mines
FLAGGED = 3 #this marks the spot as a "maybe"
MARKED = 4 #this marks it as a mine (provides protection -- can't trip a space unless this is toggled off)

#Difficulty settings: (nRows, nCols, nMines)
DIFFICULTY = {'e': (9,9,10), 
			'm':(16,16,40), 
			'h':(16,30,99)}
#### 

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
		self.status = TRIPPED
		return

	def flag(self):
		if not self.status == TRIPPED:
			#toggle status w/ UNTOUCHED
			if self.status == FLAGGED:
				self.status = UNTOUCHED
			else:
				self.status = FLAGGED
		return

	def mark(self):
		if not self.status == TRIPPED:
			#toggle status w/ UNTOUCHED
			if self.status == MARKED:
				self.status = UNTOUCHED
			else:
				self.status = MARKED
		return

class MSGame(object):
	def __init__(self,nRows,nCols,nMines):
		
		self.board = None #list of lists with BoardSpaces
		self.minePairs = None #list of all mines in self.board

		#create board (alters self.board), randomly place mines, return list of all mines (r,c pairs)
		self.minePairs = self.createBoard(nRows,nCols,nMines)

		self.nRows = nRows
		self.nCols = nCols
		self.nMines = nMines
		self.numSafeToTrip = nRows*nCols - nMines #number of spaces without a mine

		
		self.numTripped = 0 # number of spaces the user tripped
		self.gameStatus = True # indicates if the game is ongoing
		self.winStatus = False #True if user wins
		return

	@property
	def _numMarkedMines(self):
		return sum((self.board[r][c].status == MARKED for (r,c) in self.minePairs))

	@property
	def numMarkedSpaces(self):
		return sum((self.board[r][c].status == MARKED for r in xrange(self.nRows) for c in xrange(self.nCols)))

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
					board[r][c].neighbors['W'] = board[r][c-1]
					if r < nRows-1:
						board[r][c].neighbors['SW'] = board[r+1][c-1]
					if r > 0:
						board[r][c].neighbors['NW'] = board[r-1][c-1]
				if r < nRows-1:
					board[r][c].neighbors['S'] = board[r+1][c]
				if c < nCols-1:
					board[r][c].neighbors['E'] = board[r][c+1]
					if r < nRows-1:
						board[r][c].neighbors['SE'] = board[r+1][c+1]
					if r > 0:
						board[r][c].neighbors['NE'] = board[r-1][c+1]
				if r > 0:
					board[r][c].neighbors['N'] = board[r-1][c]

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
		self.minePairs = minePairs
		return minePairs #for debugging

	def tripSpace(self,r,c):
		''' - Allows the USER to trip a space, if it hasn't been "marked" 
			- If they trip a mine, they lose the game.
			- Call tripNeighbors() -- this method only does things if a space has 0 mines
			- Increment the number of tripped squares.
			- Tripping a square cannot be undone.
			- Check if the user won the game by tripping the square '''
		space = self.board[r][c]
		
		if not space.status == MARKED: #don't do anything if the space has been marked
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

		#check all mines, returning if any are NOT marked (this is less work than calculating numMarkedMines)
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

