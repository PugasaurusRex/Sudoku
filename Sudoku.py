import sys
from typing import List
import PyQt5 as pq
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
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
        self.layout.setSpacing(0)

        self.tiles = 43

        # Button to start game
        buttonStart = QPushButton(self)
        buttonStart.setText("Start Game")
        buttonStart.clicked.connect(self.parent().StartGame)
        self.layout.addWidget(buttonStart)

        # Button to exit game
        buttonExit = QPushButton(self)
        buttonExit.setText("Quit")
        buttonExit.clicked.connect(self.parent().Exit)
        self.layout.addWidget(buttonExit)

        # Difficulty combo box
        # Label
        lc = QLabel()
        lc.setText("Choose a Difficulty")
        self.layout.addWidget(lc)

        # Combo Box
        combo = QComboBox(self)
        combo.addItem("Easy")
        combo.addItem("Medium")
        combo.addItem("Hard")
        combo.addItem("Expert")
        combo.activated[str].connect(self.SetDifficulty)
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
        toolBar.addWidget(toolButton)

        toolButton = QToolButton()
        toolButton.setText("Restart")
        toolButton.setCheckable(True)
        toolButton.setAutoExclusive(True)
        toolButton.clicked.connect(self.parent().StartGame)
        toolBar.addWidget(toolButton)

        self.mistakeLabel = QLabel()

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

        # Create Background
        for i in range(0,9,3):
            for j in range(0,9,3):
                border = QFrame()
                border.setLineWidth(2)
                border.setFrameStyle(QFrame.Box)
                self.layout.addWidget(border, i, j, 3, 3)

        # Create Buttons
        for i in range(0, 9):
            for j in range(0, 9):
                temp = QPushButton("")
                temp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                temp.setFixedSize(50,50)
                temp.clicked.connect(self.ButtonClick)
                temp.installEventFilter(self)
                self.layout.addWidget(temp, i, j)
                if self.gameBoard[i][j] != '.':
                    temp.setText(str(self.gameBoard[i][j]))

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
            temp.setStyleSheet("QPushButton {background: white}")
            self.numLayout.addWidget(temp, 0, i)
            self.selectorButtons.append(temp)
            # Check to disable any completed numbers
            if self.numCount[i] == 0:
                temp.setEnabled(False)
    
        # Set selector 1 to highlighted
        self.selectorButtons[0].setStyleSheet("QPushButton {background: red}")
        self.gameLayout.addLayout(self.numLayout)

        # Create matrix for storing cell notes
        self.notes = [[[0 for i in range(9)] for j in range(9)] for k in range(9)]

    def SetNum(self):
        # Set previous button to not highlighted
        self.selectorButtons[self.curNum - 1].setStyleSheet("QPushButton {background: white}")
        # Get button index
        button = self.sender()
        idx = self.numLayout.indexOf(button)
        location = self.numLayout.getItemPosition(idx)
        # Set number from number selector
        self.curNum = location[1] + 1
        self.selectorButtons[self.curNum - 1].setStyleSheet("QPushButton {background: red}")

    def FillBoard(self):
        self.board = [[0 for i in range(9)] for j in range(9)]
        # Values available
        rows = [[a + 1 for a in range(9)] for aa in range(9)]
        cols = [[b + 1 for b in range(9)] for bb in range(9)]
        sqs = [[c + 1 for c in range(9)] for cc in range(9)]

        # Iteration counter
        iterations = 0

        for i in range(9):
            x = -1
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

        self.numSolutions = 0
        testSpots = []
        for x in range(9):
                for y in range(9):
                    self.gameBoard[x][y] = self.board[x][y]
                    testSpots.append(str(x) + "," + str(y))

        # Remove first 40 squares before checking uniqueness
        while True:
            for num in range(40):
                testIndex = random.choice(testSpots)
                testSpots.remove(testIndex)
                i = int(testIndex.split(',')[0])
                j = int(testIndex.split(',')[1])
                self.numCount[self.gameBoard[i][j] - 1] += 1
                self.gameBoard[i][j] = '.'
                self.activeTiles[i][j] = 1

            self.solveSudoku(self.gameBoard)
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
            self.solveSudoku(self.gameBoard)
            if self.numSolutions != 1:
                self.gameBoard[i][j] = self.board[i][j]
            elif self.numSolutions == 1:
                self.numCount[temp - 1] += 1
                self.activeTiles[i][j] = 1

    def GetSquare(self, x, y):
        sq = -1

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

    def solveSudoku(self, board: List[List[str]]) -> None:
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
        self.numSolutions = 0
        self.recursiveSolve(board, rowContains, colContains, sqsContains, 0, 0)

    def recursiveSolve(self, board: List[List[str]], rC: List[List[int]], cC: List[List[int]], sC: List[List[int]], row: int, col: int) -> bool:
        # Base Case
        if self.numSolutions > 1:
            return True
        if(row == 9):
            self.numSolutions += 1
            return False

        while board[row][col] != '.':
            row = self.rowCounter(row, col)
            col = self.colCounter(col)
            if(row == 9):
                self.numSolutions += 1
                return False

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
        # No valid numbers
        return False

    def rowCounter(self, row, col):
        if (col + 1) % 9 == 0:
            return row + 1
        else:
            return row

    def colCounter(self, col):
        return (col + 1) % 9

    def eventFilter(self, obj, event):
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
            button.setStyleSheet('QPushButton {color: blue;}')

    def ButtonClick(self):
         # Get button index
        button = self.sender()
        idx = self.layout.indexOf(button)
        location = self.layout.getItemPosition(idx)
        i = location[0]
        j = location[1]

        if self.activeTiles[i][j] == 1:
            button.setText(str(self.curNum))
            button.setStyleSheet('QPushButton {color: black;}')

            if self.curNum != self.board[i][j]:
                self.mistakes -= 1
                self.mistakeLabel.setText("Mistakes Left: " + str(self.mistakes))
                button.setStyleSheet('QPushButton {color: red;}')
                if self.mistakes <= 0:
                    self.GameOver()
            else:
                self.activeTiles[i][j] = 0
                # Disable the number if all are placed
                self.numCount[self.curNum - 1] -= 1
                if self.numCount[self.curNum - 1] == 0:
                    self.selectorButtons[self.curNum - 1].setStyleSheet("QPushButton {background: lightgray}")
                    self.selectorButtons[self.curNum - 1].setEnabled(False)
                    for i in range(9):
                        if self.numCount[i] != 0:
                            self.curNum = i + 1
                            self.selectorButtons[self.curNum - 1].setStyleSheet("QPushButton {background: red}")
                            break
                        elif i == 8:
                            self.Victory()

    def GameOver(self):
        msgBox = QMessageBox()
        msgBox.setText("You ran out of mistakes!")
        msgBox.setWindowTitle("Game Over")
        msgBox.setStandardButtons(QMessageBox.Retry)

        if msgBox.exec() == QMessageBox.Retry:
            self.parent().parent().StartGame()

    def Victory(self):
        msgBox = QMessageBox()
        msgBox.setText("You Win! You made "  + str(3 - self.mistakes) + " mistakes.")
        msgBox.setWindowTitle("Victory!")
        msgBox.setStandardButtons(QMessageBox.Ok)

        if msgBox.exec() == QMessageBox.Ok:
            self.parent().parent().StartGame()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = MainWindow()
    screen.show()
    sys.exit(app.exec_())