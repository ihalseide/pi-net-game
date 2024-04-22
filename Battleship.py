
sampleBoardString = "5555500000444400000033300000002220000000110000000000000000000000000000000000000000000000000000000000"

gameBoard = [0] * 100

def generateGameBoard(gameBoardString):
    if len(gameBoardString) == 100:
        for index, num in enumerate(gameBoardString):
            gameBoard[index] = num

def convertGameBoardToString(gameBoard):
    return ''.join(map(str, gameBoard))

def printGameBoard(gameBoard):
    print('=' * 19)
    for i in range(0, len(gameBoard), 10):
        print(' '.join(map(str, gameBoard[i:i+10])))

# Game setup functions

def isBoatHorizontal(front, back):
    return front[0] == back[0]

def isBoatVertical(front, back):
    return front[1] == back[1]

def getMoveNumber(move):
    if len(move) == 3:
        return 10
    else:
        return int(move[1])

def isValidBoat(front, back, boatLength):
    valid = False
    if (not isValidMove(front) or not isValidMove(back)):
        print("Invalid locations")
        return valid
    
    # Boats are placed either vertically or horizontally so either the row or the col will match
    if isBoatHorizontal(front, back):
        if len(front) == 3 and 10 - int(back[1]) + 1 == boatLength:   
            # Front is (A-J)10
            valid = True
        elif len(back) == 3 and 10 - int(front[1]) + 1 == boatLength:
            # Back is (A-J)10
            valid = True
        elif abs(int(front[1]) - int(back[1])) + 1 == boatLength:
            valid = True
    elif isBoatVertical(front, back):
        if abs(((ord(front[0].upper()) - 65) - (ord(back[0].upper()) - 65))) + 1 == boatLength:
            valid = True
    return valid

def placeShip(front, back, boatLength):
    if isValidBoat(front, back, boatLength):
        if isBoatHorizontal(front, back):
            frontNum = getMoveNumber(front)
            backNum = getMoveNumber(back)
            if (frontNum > backNum):
                # Swap front and back num
                # Ensures frontNum is less than backNum so we can move left to right across the board while placing ship
                temp = frontNum
                frontNum = backNum
                backNum = temp
            for i in range(0, (backNum + 1) - frontNum):
                makeMove(front[0] + str(i + frontNum), gameBoard, boatLength)
        else:
            # Boat is vertical
            frontChar = front[0]
            backChar = back[0]
            if (frontChar > backChar):
                # Swap front and back char move from top to bottom while placing ship
                temp = frontChar
                frontChar = backChar
                backChar = temp
            for i in range(0, (ord(backChar) - 64) - (ord(frontChar) - 65)):
                makeMove(chr(ord(frontChar) + i) + str(getMoveNumber(front)), gameBoard, boatLength)

        

# def setupGamePieces():
#     flag = false
#     while not flag:


# Functions for making a move
def isCharAthruJ(char):
    return char.upper() in 'ABCDEFGHIJ'

def isChar1thru10(char):
    return char.isdigit() and 1 <= int(char) <= 10

def isValidMove(move):
    return (len(move) == 2 or len(move) == 3) and isCharAthruJ(move[0]) and isChar1thru10(move[1])

def makeMove(move, gameBoard, charType = 'X'):
    if isValidMove(move):
        if len(move) == 2:
            moveIndex = ((ord(move[0].upper()) - 65) * 10) + (int(move[1]) - 1)
        else:
            moveIndex = ((ord(move[0].upper()) - 65) * 10) + 9 # Case that you chose 10 
        gameBoard[moveIndex] = charType
    else:
        print(move, " Is an invalid Move")
    return gameBoard




# Testing
if __name__ == '__main__':
    # generateGameBoard(sampleBoardString)
    printGameBoard(gameBoard)

    # printGameBoard(makeMove('J10', gameBoard))

    # print(convertGameBoardToString(gameBoard))
    # print(isValidBoat('a1', 'a5', 5)) # True - Check horizontal
    # print(isValidBoat('d7', 'd10', 4)) # True - Check horizontal edge case
    # print(isValidBoat('a3', 'b3', 2)) # True - Check vertical
    # print(isValidBoat('a10', 'd10', 4)) # True - Check 10 col
    # print(isValidBoat('a1', 'b1', 2)) # True
    # print(isValidBoat('a1', 'a5', 2)) # False
    # print(isValidBoat('a1', 'b2', 2)) # False
    # placeShip('j1', 'j3', 3)
    # placeShip('i10', 'i6', 5)
    placeShip('a1', 'b1', 2)
    placeShip('f10', 'j10', 5)
    printGameBoard(gameBoard)