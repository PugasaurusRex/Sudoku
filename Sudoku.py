import sys
from typing import List
import PyQt5 as pq
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtTest
import math
import random
import pprint
import time

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)

        # Set window size, title, and icon
        self.setWindowTitle("Sudoku")
        self.setWindowIcon(QIcon('Images/icon.png'))
        self.setGeometry(50, 50, 800, 800)
        self.setStyleSheet("background-color: #1e1e1e")

        # Create central widget
        self.centralWidget = QStackedWidget()
        self.setCentralWidget(self.centralWidget)

        # Tiles to remove
        self.difficultyTiles = 43

        # Set menu as central widget
        self.menuWidget = Menu(self)
        self.centralWidget.addWidget(self.menuWidget)
        self.gameWidget = None

    def StartGame(self):
        # Get difficulty from menu
        self.difficultyTiles = self.menuWidget.GetDifficulty()

        # Cleanup
        if self.gameWidget != None:
            self.centralWidget.removeWidget(self.gameWidget)
            self.gameWidget.deleteLater()
            self.gameWidget = None

        # Set game widget as central widget
        self.gameWidget = Game(self)
        self.centralWidget.addWidget(self.gameWidget)
        self.centralWidget.setCurrentWidget(self.gameWidget)

    def SetMenu(self):
        # Cleanup
        if self.menuWidget != None:
            self.centralWidget.removeWidget(self.menuWidget)
            self.menuWidget.deleteLater()
            self.menuWidget = None

        # Set menu widget as central widget
        self.menuWidget = Menu(self)
        self.centralWidget.addWidget(self.menuWidget)
        self.centralWidget.setCurrentWidget(self.menuWidget)

    def Exit(self):
        sys.exit()

class Menu(QWidget):
    def __init__(self, parent = None):
        super(Menu, self).__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setSpacing(4)

        self.tiles = 43

        # Label for title
        title = QLabel()
        title.setText("Sudoku")
        title.setStyleSheet("QLabel {color: white; padding: 15px}")
        title.setFont(QFont('forte', 70))
        self.layout.addWidget(title)

        # Button to start game
        buttonStart = QPushButton(self)
        buttonStart.setText("Start Game")
        buttonStart.clicked.connect(self.parent().StartGame)
        buttonStart.setStyleSheet("QPushButton {color: white; background-color: #1e1e1e; border-style: outset; border-color: #3e3d41; border-width: 2px; border-radius: 10px; padding: 6px;}" "QPushButton:hover { background-color: #3e3d41 }")
        self.layout.addWidget(buttonStart)

        # Button to exit game
        buttonExit = QPushButton(self)
        buttonExit.setText("Quit")
        buttonExit.clicked.connect(self.parent().Exit)
        buttonExit.setStyleSheet("QPushButton {color: white; background-color: #1e1e1e; border-style: outset; border-color: #3e3d41; border-width: 2px; border-radius: 10px; padding: 6px;}" "QPushButton:hover { background-color: #3e3d41 }")
        self.layout.addWidget(buttonExit)

        # Difficulty combo box
        # Label
        lc = QLabel()
        lc.setText("Choose a Difficulty")
        lc.setStyleSheet("QLabel {color: white}")
        self.layout.addWidget(lc)

        # Combo Box
        combo = QComboBox(self)
        combo.addItem("Easy")
        combo.addItem("Medium")
        combo.addItem("Hard")
        combo.addItem("Expert")
        combo.activated[str].connect(self.SetDifficulty)
        combo.setStyleSheet("QComboBox {color: white; background-color: #3e3d41;}" "QComboBox QAbstractItemView {color: white; background: #3e3d41; selection-background-color: #3e3d41;}")
        self.layout.addWidget(combo)

    def SetDifficulty(self, text):
        if text == 'Easy':
            self.tiles = 43
        if text == 'Medium':
            self.tiles = 51
        if text == 'Hard':
            self.tiles = 56
        if text == 'Expert':
            self.tiles = 58

    def GetDifficulty(self) -> int:
        return self.tiles

class Game(QWidget):
    def __init__(self, parent = None):
        super(Game, self).__init__(parent)
        self.layout = QGridLayout()
        self.gameLayout = QVBoxLayout()
        self.setLayout(self.gameLayout)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setSpacing(0)

        size = screen.size().height() - 200
        self.layout.maximumSize().setHeight(size)
        self.layout.maximumSize().setWidth(size)
        self.layout.setSizeConstraint(QLayout.SetMaximumSize)
        self.gameLayout.addLayout(self.layout)

        # Create toolbar
        toolBar = QToolBar()
        self.gameLayout.setMenuBar(toolBar)

        # Add items to toolbar
        toolButton = QToolButton()
        toolButton.setText("Menu")
        toolButton.setCheckable(True)
        toolButton.setAutoExclusive(True)
        toolButton.clicked.connect(self.parent().SetMenu)
        toolButton.setStyleSheet("QToolButton {color: white; background-color: #1e1e1e; padding: 6px;}" "QToolButton:hover { background-color: #3e3d41 }")
        toolBar.addWidget(toolButton)

        toolButton = QToolButton()
        toolButton.setText("Restart")
        toolButton.setCheckable(True)
        toolButton.setAutoExclusive(True)
        toolButton.clicked.connect(self.parent().StartGame)
        toolButton.setStyleSheet("QToolButton {color: white; background-color: #1e1e1e; padding: 6px;}" "QToolButton:hover { background-color: #3e3d41 }")
        toolBar.addWidget(toolButton)

        self.mistakeLabel = QLabel()
        self.mistakeLabel.setStyleSheet("QLabel {color: white}")

        # Var for number of mistakes that can be made
        self.mistakes = 3

        self.mistakeLabel.setText("Mistakes Left: " + str(self.mistakes))
        toolBar.addWidget(self.mistakeLabel)

        start = time.time()

        # Lists for board
        self.defaultR = [1,2,3,4,5,6,7,8,9]
        self.gameBoard = [[0 for i in range(9)] for j in range(9)]

        # Create list to keep track of how many each number is left
        # Used to disable button of numbers that are complete.
        self.numCount = [0 for i in range(9)]

        # Call functions to create board
        self.FillBoard()
        self.RemoveSquares(self.parent().difficultyTiles)

        end = time.time()
        print("Time to generate board: " + str(end - start))

        # Create Buttons
        self.buttons = [[0 for i in range(9)] for i in range(9)]
        for i in range(0, 9):
            for j in range(0, 9):
                temp = QPushButton("")
                temp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                temp.setFixedSize(50,50)
                temp.clicked.connect(self.ButtonClick)
                temp.installEventFilter(self)
                self.layout.addWidget(temp, i, j, Qt.Alignment(Qt.AlignCenter))
                temp.setStyleSheet("QPushButton {color: white; background-color: #017acc;}" "QPushButton:hover { background-color: #61c9fd }")
                if self.gameBoard[i][j] != '.':
                    temp.setText(str(self.gameBoard[i][j]))

                self.buttons[i][j] = temp

        # Create Background Lines
        # Place horizontal lines
        for i in range(0, 10, 3):
            border = QFrame()
            border.setLineWidth(3)
            border.setStyleSheet("QFrame {color: #3e3d41}")
            border.setFrameStyle(QFrame.HLine)
            self.layout.addWidget(border, i, 0, i, 9, Qt.Alignment(Qt.AlignTop))

        # Place vertical lines
        for i in range(0, 10, 3):
            border = QFrame()
            border.setLineWidth(4)
            border.setStyleSheet("QFrame {color: #3e3d41}")
            border.setFrameStyle(QFrame.VLine)
            self.layout.addWidget(border, 0, i, 9, i, Qt.Alignment(Qt.AlignLeft))

        # Current Number Selected
        self.curNum = 1
        
        # Layout for number selector
        self.numLayout = QGridLayout()
        self.numLayout.setAlignment(Qt.AlignCenter)
        self.numLayout.setSpacing(0)

        self.numLayout.maximumSize().setHeight(size)
        self.numLayout.maximumSize().setWidth(size)
        self.numLayout.setSizeConstraint(QLayout.SetMaximumSize)

        # Create number selector buttons
        self.selectorButtons = []
        for i in range(0, 9):
            temp = QPushButton(str(i + 1))
            temp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            temp.setFixedSize(50,50)
            temp.clicked.connect(self.SetNum)
            temp.setStyleSheet("QPushButton {color: white; background-color: #017acc;}" "QPushButton:hover { background-color: #61c9fd }")
            self.numLayout.addWidget(temp, 0, i)
            self.selectorButtons.append(temp)
            # Check to disable any completed numbers
            if self.numCount[i] == 0:
                temp.setEnabled(False)
    
        # Set selector 1 to highlighted
        self.selectorButtons[0].setStyleSheet("QPushButton {color: white; background-color: #61c9fd;}" "QPushButton:hover { background-color: #61c9fd }")
        self.gameLayout.addLayout(self.numLayout)

        # Create matrix for storing manual cell notes
        self.notes = [[[0 for i in range(9)] for j in range(9)] for k in range(9)]

        # Layout for solvers
        self.solverLayout = QGridLayout()
        self.solverLayout.setAlignment(Qt.AlignCenter)
        self.solverLayout.setSpacing(2)
        self.solverLayout.maximumSize().setHeight(size)
        self.solverLayout.maximumSize().setWidth(size)
        self.solverLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.gameLayout.addLayout(self.solverLayout)

        # Create Buttons for algorithm solvers
        self.recursiveButton = QPushButton("Recursive Solver")
        self.solverLayout.addWidget(self.recursiveButton)
        self.recursiveButton.clicked.connect(lambda: self.solveSudoku(self.gameBoard, True, True))
        self.recursiveButton.setStyleSheet("QPushButton {color: white; background-color: #1e1e1e; border-style: outset; border-color: #3e3d41; border-width: 2px; border-radius: 10px; padding: 6px;}" "QPushButton:hover { background-color: #3e3d41 }")
        self.recursiveButton.setMaximumWidth(size)

        self.noteButton = QPushButton("Note Solver")
        self.solverLayout.addWidget(self.noteButton)
        self.noteButton.clicked.connect(lambda: self.solveSudoku(self.gameBoard, True, False))
        self.noteButton.setStyleSheet("QPushButton {color: white; background-color: #1e1e1e; border-style: outset; border-color: #3e3d41; border-width: 2px; border-radius: 10px; padding: 6px;}" "QPushButton:hover { background-color: #3e3d41 }")
        self.noteButton.setMaximumWidth(size)

        # Slider for changing time between algorithm iterations
        self.iSlider = QSlider(Qt.Horizontal)
        self.iSlider.setMinimum(0)
        self.iSlider.setMaximum(3000)
        self.iSlider.setValue(20)
        self.iSlider.setSingleStep(10)
        self.iSlider.valueChanged.connect(lambda: self.SetInterval(self.iSlider.value()))
        self.iSlider.setMaximumWidth(size - 300)

        # Label for slider
        self.intervalLabel = QLabel()
        self.intervalLabel.setText("Interval Between Iterations: 20 milliseconds")
        self.intervalLabel.setStyleSheet("QLabel {color: white}")
        self.intervalLabel.setAlignment(Qt.AlignCenter)

        # Add label and slider to layout
        self.solverLayout.addWidget(self.intervalLabel)
        self.solverLayout.addWidget(self.iSlider)

        # Variable for time between iterations
        self.time = 20

    def SetInterval(self, value):
        # Change time from slider to seconds and store value
        self.time = self.iSlider.value()
        self.intervalLabel.setText("Interval Between Iterations: " + str(self.time) + " milliseconds")

    def SetNum(self):
        # Set previous button to not highlighted
        self.selectorButtons[self.curNum - 1].setStyleSheet("QPushButton {color: white; background-color: #017acc;}" "QPushButton:hover { background-color: #61c9fd }")
        # Get button index
        button = self.sender()
        idx = self.numLayout.indexOf(button)
        location = self.numLayout.getItemPosition(idx)
        # Set number from number selector
        self.curNum = location[1] + 1
        self.selectorButtons[self.curNum - 1].setStyleSheet("QPushButton {color: white; background-color: #61c9fd;}" "QPushButton:hover { background-color: #61c9fd }")

    def FillBoard(self):
        self.board = [[0 for i in range(9)] for j in range(9)]
        # Values available
        rows = [[a + 1 for a in range(9)] for aa in range(9)]
        cols = [[b + 1 for b in range(9)] for bb in range(9)]
        sqs = [[c + 1 for c in range(9)] for cc in range(9)]

        # Iteration counter
        iterations = 0

        for i in range(9):
            # Value for checking infinite loops
            x = -1
            # j counter
            j = 0
            while j < 9:
                while True:
                    iterations += 1
                    # If iterations get to high call fill board again
                    if(iterations > 5000):
                        self.FillBoard()
                        return

                    lastX = x

                    # Get random value from row
                    x = random.choice(rows[i])
                    sq = self.GetSquare(i,j)
                    # If valid set it to square
                    if x in cols[j] and x in sqs[sq]:
                        rows[i].remove(x)
                        cols[j].remove(x)
                        sqs[sq].remove(x)
                        self.board[i][j] = x
                        j += 1
                        break
                    # If value repeating, restart row
                    elif lastX == x:
                        rows[i].clear()
                        rows[i].extend(self.defaultR)
                        j = 0
                        for k in range(9):
                            if self.board[i][k] != 0:
                                cols[k].append(self.board[i][k])
                                sqs[self.GetSquare(i,k)].append(self.board[i][k])
                                self.board[i][k] = 0
                                x = -1
                            else:
                                break

    def RemoveSquares(self, numRemove):
        # Matrix for active tiles
        self.activeTiles = [[0 for i in range(9)] for j in range(9)]

        self.numLeft = numRemove

        # Create new gameboard from already solved board
        self.numSolutions = 0
        testSpots = []
        for x in range(9):
                for y in range(9):
                    self.gameBoard[x][y] = self.board[x][y]
                    testSpots.append(str(x) + "," + str(y))

        # Remove first 40 tiles before checking uniqueness
        while True:
            # Remove 40 tiles
            for num in range(40):
                testIndex = random.choice(testSpots)
                testSpots.remove(testIndex)
                i = int(testIndex.split(',')[0])
                j = int(testIndex.split(',')[1])
                self.numCount[self.gameBoard[i][j] - 1] += 1
                self.gameBoard[i][j] = '.'
                self.activeTiles[i][j] = 1

            # Check uniqueness with recursion
            self.solveSudoku(self.gameBoard, False, True)

            # If not unique reset gameboard and try again
            if self.numSolutions != 1:
                self.activeTiles = [[0 for i in range(9)] for j in range(9)]
                self.numCount = [0 for i in range(9)]
                testSpots = []
                for x in range(9):
                        for y in range(9):
                            self.gameBoard[x][y] = self.board[x][y]
                            testSpots.append(str(x) + "," + str(y))
            elif self.numSolutions == 1:
                break

        # Check board uniqueness after each square removed
        # If the randomly chosen square removes board uniqueness it is not removed
        for num in range(numRemove - 40):               
            testIndex = random.choice(testSpots)
            testSpots.remove(testIndex)
            i = int(testIndex.split(',')[0])
            j = int(testIndex.split(',')[1])
            temp = self.gameBoard[i][j]
            self.gameBoard[i][j] = '.'
            self.solveSudoku(self.gameBoard, False, True)
            if self.numSolutions != 1:
                self.gameBoard[i][j] = self.board[i][j]
            elif self.numSolutions == 1:
                self.numCount[temp - 1] += 1
                self.activeTiles[i][j] = 1

    def GetSquare(self, x, y):
        sq = -1
        # Return the square based on the given indices
        if(x < 3 and y < 3):
            sq = 0

        if(x < 3 and y < 6 and y > 2):
            sq = 1

        if(x < 3 and y > 5):
            sq = 2

        if(x > 2 and x < 6 and y < 3):
            sq = 3

        if(x > 2 and x < 6 and y > 2 and y < 6):
            sq = 4

        if(x > 2 and x < 6 and y > 5):
            sq = 5

        if(x > 5 and y < 3):
            sq = 6

        if(x > 5 and y < 6 and y > 2):
            sq = 7

        if(x > 5 and y > 5):
            sq = 8

        return sq

    def solveSudoku(self, board: List[List[str]], visual: bool, recursive: bool) -> None:
        if visual:
            # If visual solve is used, disable all buttons
            self.recursiveButton.setEnabled(False)
            self.noteButton.setEnabled(False)

            for i in range(9):
                self.selectorButtons[i].setEnabled(False)
                self.selectorButtons[i].setStyleSheet("QPushButton {color: white; background-color: #0008ff;}" "QPushButton:hover { background-color: #0008ff }")
                for j in range(9):
                    self.activeTiles[i][j] = 1
                    self.buttons[i][j].setEnabled(False)

        if recursive:
            # Lists for storing the contents of rows, columns, and squares
            rowContains = [[0 for i in range(9)]for i in range(9)]
            colContains = [[0 for i in range(9)]for i in range(9)]
            sqsContains = [[0 for i in range(9)]for i in range(9)]

            # Get values for each row, column, and square completion
            for i in range(9):
                for j in range(9):
                    if board[i][j] != '.':
                        idx = int(board[i][j]) - 1
                        rowContains[i][idx] = 1
                        colContains[j][idx] = 1
                        sqsContains[self.GetSquare(i,j)][idx] = 1
        
            # Start recursive solve
            if visual:
                self.visualSolve(board, rowContains, colContains, sqsContains, 0, 0)
            else:
                self.numSolutions = 0
                self.recursiveSolve(board, rowContains, colContains, sqsContains, 0, 0)

        else:
            self.noteSolve(board)

    def recursiveSolve(self, board: List[List[str]], rC: List[List[int]], cC: List[List[int]], sC: List[List[int]], row: int, col: int) -> bool:
        # Base Case
        if self.numSolutions > 1:
            return True
        if(row == 9):
            self.numSolutions += 1
            return False

        # Loop until next unsolved tile
        while board[row][col] != '.':
            row = self.rowCounter(row, col)
            col = self.colCounter(col)
            if(row == 9):
                self.numSolutions += 1
                return False

        # When unsolved tile is found loop through 1 to 9
        for i in range(9):
            # If number is valid set it on the board
            if rC[row][i] == 0 and cC[col][i] == 0 and sC[self.GetSquare(row,col)][i] == 0:
                rC[row][i] = 1
                cC[col][i] = 1
                sC[self.GetSquare(row,col)][i] = 1

                # If game is completed return true; otherwise reset and try next value
                if(self.recursiveSolve(board, rC, cC, sC, self.rowCounter(row, col), self.colCounter(col))):
                    return True
                else:
                    rC[row][i] = 0
                    cC[col][i] = 0
                    sC[self.GetSquare(row,col)][i] = 0
        # No valid numbers, return false for backtracking
        return False

    def visualSolve(self, board: List[List[str]], rC: List[List[int]], cC: List[List[int]], sC: List[List[int]], row: int, col: int) -> bool:
        try:
            # Base Case
            if(row == 9):
                return True

            # Loop until next unsolved tile
            while board[row][col] != '.':
                row = self.rowCounter(row, col)
                col = self.colCounter(col)
                if(row == 9):
                    return True

            # When unsolved tile is found loop through 1 to 9
            for i in range(9):
                # Update UI
                self.buttons[row][col].setText(str(i + 1))
                self.buttons[row][col].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")
                QtTest.QTest.qWait(self.time)

                # If number is valid set it on the board
                if rC[row][i] == 0 and cC[col][i] == 0 and sC[self.GetSquare(row,col)][i] == 0:
                    board[row][col] = i + 1
                    rC[row][i] = 1
                    cC[col][i] = 1
                    sC[self.GetSquare(row,col)][i] = 1

                    # If game is completed return true; otherwise reset and try another value
                    if(self.visualSolve(board, rC, cC, sC, self.rowCounter(row, col), self.colCounter(col))):
                        return True
                    else:
                        rC[row][i] = 0
                        cC[col][i] = 0
                        sC[self.GetSquare(row,col)][i] = 0
            # If looped through all values and no valid one found return false for backtracking
            board[row][col] = '.'
            # Update UI
            self.buttons[row][col].setText("")
            self.buttons[row][col].setStyleSheet("QPushButton {color: white; background-color: red;}")
            QtTest.QTest.qWait(self.time)

            return False
        
        except:
            print("Forcefully stopping solver due to restart or board wipe.")

    def noteSolve(self, board: List[List[str]]) -> None:
        # Solve sudoku puzzle that is assumed possible with one solution
        # Find all possible answers for each un-solved cell
        # Determine if there is any cell that is definitely a number
        # eg. only spot for a 5 in a row, square, or column
        # Set that number and update effected notes. Then repeat until solved

        try:
            # Lists for storing the contents of rows, columns, and squares
            self.rowContains = [[]for i in range(9)]
            self.colContains = [[]for i in range(9)]
            self.sqContains = [[]for i in range(9)]

            # List for storing the possible values of each cell
            tilesToSolve = [[[] for i in range(9)] for i in range(9)]

            # Counter to determine how many cells are left to solve
            cellsLeft = 0

            # Get values for each row, column, and square completion
            for i in range(9):
                for j in range(9):
                    if board[i][j] != '.':
                        idx = int(board[i][j])
                        self.rowContains[i].append(idx)
                        self.colContains[j].append(idx)
                        self.sqContains[self.GetSquare(i,j)].append(idx)

            # Set all possible numbers to list for each unsolved cells
            for i in range(9):
                for j in range(9):
                    if board[i][j] == '.':
                        cellsLeft += 1
                        for k in range(9):
                            x = k + 1
                            if x not in self.rowContains[i] and x not in self.colContains[j] and x not in self.sqContains[self.GetSquare(i,j)]:
                                tilesToSolve[i][j].append(x)

                                # Visual: Set current number and call right click for button
                                self.curNum = x
                                self.RightButton(self.buttons[i][j])
                                # Update UI
                                self.buttons[i][j].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")
                                QtTest.QTest.qWait(self.time)

            # Repurpose col, row, and sq used to count number of possible tiles
            self.rowContains = [[0 for i in range(9)]for i in range(9)]
            self.colContains = [[0 for i in range(9)]for i in range(9)]
            self.sqContains = [[0 for i in range(9)]for i in range(9)]

            # Count the amount of each number per region
            for i in range(9):
                for j in range(9):
                    if board[i][j] == '.':
                        for num in range(len(tilesToSolve[i][j])):
                                    idx = tilesToSolve[i][j][num] - 1
                                    self.rowContains[i][idx] += 1
                                    self.colContains[j][idx] += 1
                                    self.sqContains[self.GetSquare(i,j)][idx] += 1

            # Begin Solving
            while cellsLeft > 0:
                cellsOld = cellsLeft
                # Loop through board
                for i in range(9):
                    for j in range(9):
                        # Only stop at un-solved cells
                        if board[i][j] == '.':
                            # Check 1: Only one possible number for cell
                            self.buttons[i][j].setStyleSheet("QPushButton {color: white; background-color: lightgreen;}")
                            if len(tilesToSolve[i][j]) == 1:
                                num = tilesToSolve[i][j][0]
                                board[i][j] = num
                                tilesToSolve[i][j] = []
                                cellsLeft -= 1

                                self.rowContains[i][num - 1] = 0
                                self.colContains[j][num - 1] = 0
                                self.sqContains[self.GetSquare(i,j)][num - 1] = 0

                                # Set button text
                                self.buttons[i][j].setText(str(num))

                                # Remove number from row, col, and square
                                tilesToSolve = self.removeVal(i, j, self.GetSquare(i,j), int(board[i][j]), tilesToSolve)

                            # Update UI
                            QtTest.QTest.qWait(self.time)
                            # If solved set to blue
                            if tilesToSolve[i][j] == []:
                                self.buttons[i][j].setStyleSheet("QPushButton {color: white; background-color: #017acc;}")
                            else:
                                self.buttons[i][j].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")
                      
                # When all single tiles are filled move to check 2
                if cellsLeft == cellsOld and cellsLeft > 0:
                    # Check 2: Check each row, col, or square to see if it has a tile with only one answer
                    for i in range(9):
                        # Check row i
                        if self.rowContains[i].count(1) > 0:
                            # Get number from index
                            num = self.rowContains[i].index(1) + 1
                            # Find tile in row that has the number and set it
                            for j in range(9):
                                self.buttons[i][j].setStyleSheet("QPushButton {color: white; background-color: lightgreen;}")
                                if board[i][j] == '.' and num in tilesToSolve[i][j]:
                                    board[i][j] = num
                                    tilesToSolve[i][j] = []
                                    cellsLeft -= 1

                                    # Remove number from possible values in its region
                                    self.rowContains[i][num - 1] = 0
                                    self.colContains[j][num - 1] = 0
                                    self.sqContains[self.GetSquare(i,j)][num - 1] = 0

                                    # Set button text
                                    self.buttons[i][j].setText(str(num))

                                    # Remove number from row, col, and square
                                    tilesToSolve = self.removeVal(i, j, self.GetSquare(i,j), int(num), tilesToSolve)

                                    # Update UI
                                    QtTest.QTest.qWait(self.time)
                                    # If solved set to blue
                                    if tilesToSolve[i][j] == []:
                                        self.buttons[i][j].setStyleSheet("QPushButton {color: white; background-color: #017acc;}")
                                    else:
                                        self.buttons[i][j].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")

                                    break

                                # Update UI
                                QtTest.QTest.qWait(self.time)
                                # If solved set to blue
                                if tilesToSolve[i][j] == []:
                                    self.buttons[i][j].setStyleSheet("QPushButton {color: white; background-color: #017acc;}")
                                else:
                                    self.buttons[i][j].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")

                        # If none in row check col i
                        elif self.colContains[i].count(1) > 0:
                                # Find number from index
                                num = self.colContains[i].index(1) + 1
                                # Find tile in column that has the number and set it
                                for j in range(9):
                                    self.buttons[j][i].setStyleSheet("QPushButton {color: white; background-color: lightgreen;}")
                                    if board[j][i] == '.' and num in tilesToSolve[j][i]:
                                        board[j][i] = num
                                        tilesToSolve[j][i] = []
                                        cellsLeft -= 1

                                        # Remove number from possible values in its region
                                        self.rowContains[j][num - 1] = 0
                                        self.colContains[i][num - 1] = 0
                                        self.sqContains[self.GetSquare(j,i)][num - 1] = 0

                                        # Set button text
                                        self.buttons[j][i].setText(str(num))

                                        # Remove number from row, col, and square
                                        tilesToSolve = self.removeVal(j, i, self.GetSquare(j,i), int(num), tilesToSolve)

                                        # Update UI
                                        QtTest.QTest.qWait(self.time)
                                        # If solved set to blue
                                        if tilesToSolve[j][i] == []:
                                            self.buttons[j][i].setStyleSheet("QPushButton {color: white; background-color: #017acc;}")
                                        else:
                                            self.buttons[j][i].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")

                                        break

                                    # Update UI
                                    QtTest.QTest.qWait(self.time)
                                    # If solved set to blue
                                    if tilesToSolve[j][i] == []:
                                        self.buttons[j][i].setStyleSheet("QPushButton {color: white; background-color: #017acc;}")
                                    else:
                                        self.buttons[j][i].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")
                        
                        # If no tiles in row or col check square i
                        elif self.sqContains[i].count(1) > 0:
                                # Get number from index
                                num = self.sqContains[i].index(1) + 1

                                # Get start indices of square i
                                sq = i
                                if sq == 0:
                                  starti = 0
                                  startj = 0
                                elif sq == 1:
                                  starti = 0
                                  startj = 3
                                elif sq == 2:
                                  starti = 0
                                  startj = 6
                                elif sq == 3:
                                  starti = 3
                                  startj = 0
                                elif sq == 4:
                                  starti = 3
                                  startj = 3
                                elif sq == 5:
                                  starti = 3
                                  startj = 6
                                elif sq == 6:
                                  starti = 6
                                  startj = 0
                                elif sq == 7:
                                  starti = 6
                                  startj = 3
                                elif sq == 8:
                                  starti = 6
                                  startj = 6

                                # From start indices loop through square and find tile with number and set it
                                for x in range(starti, starti + 3):
                                        for y in range(startj, startj + 3):
                                            self.buttons[x][y].setStyleSheet("QPushButton {color: white; background-color: lightgreen;}")
                                            if board[x][y] == '.' and num in tilesToSolve[x][y]:
                                
                                                board[x][y] = num
                                                tilesToSolve[x][y] = []
                                                cellsLeft -= 1

                                                # Remove number from possible values in its region
                                                self.rowContains[x][num - 1] = 0
                                                self.colContains[y][num - 1] = 0
                                                self.sqContains[sq][num - 1] = 0

                                                # Set button text
                                                self.buttons[x][y].setText(str(num))

                                                # Remove number from row, col, and square
                                                tilesToSolve = self.removeVal(x, y, sq, int(num), tilesToSolve)

                                                # Update UI
                                                QtTest.QTest.qWait(self.time)
                                                # If solved set to blue
                                                if tilesToSolve[x][y] == []:
                                                    self.buttons[x][y].setStyleSheet("QPushButton {color: white; background-color: #017acc;}")
                                                else:
                                                    self.buttons[x][y].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")

                                                break

                                            # Update UI
                                            QtTest.QTest.qWait(self.time)
                                            # If solved set to blue
                                            if tilesToSolve[x][y] == []:
                                                self.buttons[x][y].setStyleSheet("QPushButton {color: white; background-color: #017acc;}")
                                            else:
                                                self.buttons[x][y].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")

                # If there are no single tiles left move to recursive solve
                # Could expand algorithm to check for tiles that are identical but recursion is most likely faster
                # e.g. a row has two tiles with (7,2) it can be assumed that all other tiles in row are not 7 or 2
                if cellsLeft == cellsOld and cellsLeft > 0:
                    print("Moving to recursive!")
                    self.solveSudoku(board, True, True)
                    break

        except:
            print("Forcefully stopping solver due to reset or board wipe.")

    def removeVal(self, i, j, sq, val, cellBoard: List[List[List[str]]]):
        try:
            # Remove from row and column
            for a in range(9):
                if val in cellBoard[i][a]:
                    cellBoard[i][a].remove(val)
                    self.rowContains[i][val-1] -= 1

                    # Update notes for UI
                    self.curNum = val
                    self.RightButton(self.buttons[i][a])

                if val in cellBoard[a][j]:
                    cellBoard[a][j].remove(val)
                    self.colContains[j][val-1] -= 1

                    # Update notes for UI
                    self.curNum = val
                    self.RightButton(self.buttons[a][j])

                # Update UI
                self.buttons[i][a].setStyleSheet("QPushButton {color: white; background-color: lightgreen;}")
                self.buttons[a][j].setStyleSheet("QPushButton {color: white; background-color: lightgreen;}")
                QtTest.QTest.qWait(self.time)
                # If it is starting tile: keep light green; if tile is already solved keep blue; if tile is yet to be solved set back to green
                if a == j:
                    self.buttons[i][a].setStyleSheet("QPushButton {color: white; background-color: lightgreen;}")
                else:
                    if cellBoard[i][a] == []:
                        self.buttons[i][a].setStyleSheet("QPushButton {color: white; background-color: #017acc;}")
                    else:
                        self.buttons[i][a].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")

                if a == i:
                    self.buttons[a][j].setStyleSheet("QPushButton {color: white; background-color: lightgreen;}")
                else:
                    if cellBoard[a][j] == []:
                        self.buttons[a][j].setStyleSheet("QPushButton {color: white; background-color: #017acc;}")
                    else:
                        self.buttons[a][j].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")

            # Remove from square
            if sq == 0:
              starti = 0
              startj = 0
            elif sq == 1:
              starti = 0
              startj = 3
            elif sq == 2:
              starti = 0
              startj = 6
            elif sq == 3:
              starti = 3
              startj = 0
            elif sq == 4:
              starti = 3
              startj = 3
            elif sq == 5:
              starti = 3
              startj = 6
            elif sq == 6:
              starti = 6
              startj = 0
            elif sq == 7:
              starti = 6
              startj = 3
            elif sq == 8:
              starti = 6
              startj = 6

            for x in range(starti, starti + 3):
                    for y in range(startj, startj + 3):
                        if val in cellBoard[x][y]:
                            cellBoard[x][y].remove(val)
                            self.sqContains[sq][val-1] -= 1

                            # Update notes for UI
                            self.curNum = val
                            self.RightButton(self.buttons[x][y])

                        # Update UI
                        self.buttons[x][y].setStyleSheet("QPushButton {color: white; background-color: lightgreen;}")
                        QtTest.QTest.qWait(self.time)
                        if x == i and y == j:
                            self.buttons[x][y].setStyleSheet("QPushButton {color: white; background-color: lightgreen;}")
                        else:
                            if cellBoard[x][y] == []:
                                self.buttons[x][y].setStyleSheet("QPushButton {color: white; background-color: #017acc;}")
                            else:
                                self.buttons[x][y].setStyleSheet("QPushButton {color: white; background-color: #567f4e;}")

            return cellBoard
        except:
            print("Could not find board or necessary matrix.")

    def rowCounter(self, row, col):
        if (col + 1) % 9 == 0:
            return row + 1
        else:
            return row

    def colCounter(self, col):
        return (col + 1) % 9

    def eventFilter(self, obj, event):
        # If user right clicks call the right click custom function
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                self.RightButton(obj)
        return QObject.event(obj, event)

    def RightButton(self, obj):
        # Get button index
        button = obj
        idx = self.layout.indexOf(button)
        location = self.layout.getItemPosition(idx)
        i = location[0]
        j = location[1]

        # Only allow notes if tile is active
        if self.activeTiles[i][j] == 1:
            text = ""
            # Toggle note for current number
            if self.notes[i][j][self.curNum - 1] == 0:
                self.notes[i][j][self.curNum - 1] = 1
            else:
                self.notes[i][j][self.curNum - 1] = 0

            # Create text format for button text
            for x in range(9):
                if self.notes[i][j][x] == 1:
                    text += str(x+1)
                else:
                    text += " "

                text += " "
                if x == 2 or x == 5:
                    text += "\n"
            
            # Set the button text
            button.setText(text)
            button.setStyleSheet("QPushButton {color: white; background-color: #017acc;}" "QPushButton:hover { background-color: #61c9fd }")

    def ButtonClick(self):
         # Get button index
        button = self.sender()
        idx = self.layout.indexOf(button)
        location = self.layout.getItemPosition(idx)
        i = location[0]
        j = location[1]

        # If tile is not solved set to current number
        if self.activeTiles[i][j] == 1:
            button.setText(str(self.curNum))
            button.setStyleSheet("QPushButton {color: white; background-color: #017acc;}" "QPushButton:hover { background-color: #61c9fd }")

            # If current number is not correct decrease mistake counter and check for game over
            if self.curNum != self.board[i][j]:
                self.mistakes -= 1
                self.mistakeLabel.setText("Mistakes Left: " + str(self.mistakes))
                button.setStyleSheet("QPushButton {color: red; background-color: #017acc;}" "QPushButton:hover { background-color: #61c9fd }")
                if self.mistakes <= 0:
                    self.GameOver()
            # If current number is correct decrease numbers left and check victory
            else:
                self.activeTiles[i][j] = 0
                # Disable the number if all are placed
                self.numCount[self.curNum - 1] -= 1
                # If there are none of current number left disable the selector button for number
                if self.numCount[self.curNum - 1] == 0:
                    self.selectorButtons[self.curNum - 1].setStyleSheet("QPushButton {color: white; background-color: #0008ff;}" "QPushButton:hover { background-color: #0008ff }")
                    self.selectorButtons[self.curNum - 1].setEnabled(False)
                    # Loop through numbers and set selector for current number to first available value
                    # If no values are left the player has won, call victory function
                    for i in range(9):
                        if self.numCount[i] != 0:
                            self.curNum = i + 1
                            self.selectorButtons[self.curNum - 1].setStyleSheet("QPushButton {color: white; background-color: #61c9fd;}" "QPushButton:hover { background-color: #61c9fd }")
                            break
                        # If there are no numbers left the player wins
                        elif i == 8:
                            self.Victory()

    def GameOver(self):
        msgBox = QMessageBox()
        msgBox.setText("You ran out of mistakes!")
        msgBox.setWindowTitle("Game Over")
        msgBox.setWindowIcon(QIcon("Images/icon.png"))
        msgBox.setStandardButtons(QMessageBox.Retry)
        msgBox.setStyleSheet("QMessageBox {background-color: #1e1e1e}"
                             "QMessageBox QLabel {color: white}"
                             "QMessageBox QPushButton {color: white; background-color: #1e1e1e; border-style: outset; border-color: #3e3d41; border-width: 2px; border-radius: 10px; padding: 10px;}"
                             "QMessageBox QPushButton:hover { background-color: #3e3d41 }")

        if msgBox.exec() == QMessageBox.Retry:
            self.parent().parent().StartGame()

    def Victory(self):
        msgBox = QMessageBox()
        msgBox.setText("You Win! You made "  + str(3 - self.mistakes) + " mistakes.")
        msgBox.setWindowTitle("Victory!")
        msgBox.setWindowIcon(QIcon("Images/icon.png"))
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setStyleSheet("QMessageBox {background-color: #1e1e1e}"
                             "QMessageBox QLabel {color: white}"
                             "QMessageBox QPushButton {color: white; background-color: #1e1e1e; border-style: outset; border-color: #3e3d41; border-width: 2px; border-radius: 10px; padding: 10px;}"
                             "QMessageBox QPushButton:hover { background-color: #3e3d41 }")

        if msgBox.exec() == QMessageBox.Ok:
            self.parent().parent().StartGame()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = MainWindow()
    screen.show()
    sys.exit(app.exec_())