
sampleBoardString = "5555500000444400000033300000002220000000110000000000000000000000000000000000000000000000000000000000"

gameBoard = [0] * 100

def generateGameBoard(gameBoardString):
    if len(gameBoardString) == 100:
        for index, num in enumerate(gameBoardString):
            gameBoard[index] = num

def convertGameBoardToString(gameBoard):
    return ''.join(map(str, gameBoard))

def printGameBoard(gameBoard):
    for i in range(0, len(gameBoard), 10):
        print(' '.join(map(str, gameBoard[i:i+10])))

# Functions for making a move
def isCharAthruJ(char):
    return char.upper() in 'ABCDEFGHIJ'

def isChar1thru10(char):
    return char.isdigit() and 1 <= int(char) <= 10

def isValidMove(move):
    return (len(move) == 2 or len(move) == 3) and isCharAthruJ(move[0]) and isChar1thru10(move[1])

def makeMove(move, gameBoard):
    if isValidMove(move):
        if len(move) == 2:
            moveIndex = ((ord(move[0].upper()) - 65) * 10) + (int(move[1]) - 1)
        else:
            moveIndex = ((ord(move[0].upper()) - 65) * 10) + 9 # Case that you chose 10 
        gameBoard[moveIndex] = 'X'
    else:
        print("Invalid Move")
    return gameBoard




# Testing
generateGameBoard(sampleBoardString)
printGameBoard(gameBoard)

printGameBoard(makeMove('J10', gameBoard))

print(convertGameBoardToString(gameBoard))