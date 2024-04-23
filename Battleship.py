personalGameBoard = [0] * 100 # Your personal game board with your ships 
hitMissBoard = [0] * 100 # Will display your moves and whether they were hits or misses
enemyGameBoard = [0] * 100 # Used to determine whether your moves hit or missed, but will never be displayed

# List of boats used in determining when all boats are sunk (order: destroyer, submarine, cruiser, battleship, carrier)
enemyBoatLog = [2, 3, 3, 4, 5] 
personalBoatLog = [2, 3, 3, 4, 5]

monospace_digit_three = "\U0001D7F9" # Alternate 3 

sampleBoardString = "555550000044440000003330000000" + monospace_digit_three + monospace_digit_three + monospace_digit_three + "0000000220000000000000000000000000000000000000000000000000000000000"

# Game setup functions

def processEnemyMove(enemyMove):
    if isValidMove(enemyMove):
        if len(enemyMove) == 2:
            moveIndex = ((ord(enemyMove[0].upper()) - 65) * 10) + (int(enemyMove[1]) - 1)
        else:
            moveIndex = ((ord(enemyMove[0].upper()) - 65) * 10) + 9 # Case that you chose 10

        if personalGameBoard[moveIndex] != '0':
            updatePersonalBoatLog(personalGameBoard[moveIndex]) # Parameter tells us which boat was hit
            isGameOver(personalBoatLog)

def updatePersonalBoatLog(charType):
    if charType == '2':
        personalBoatLog[0] -= 1

    elif charType == monospace_digit_three:
        personalBoatLog[1] -= 1

    elif charType == '3':
        personalBoatLog[2] -= 1

    elif charType == '4':
        personalBoatLog[3] -= 1

    elif charType == '5':
        personalBoatLog[4] -= 1


def generateEnemyGameBoard(gameBoardString):
    if len(gameBoardString) == 100:
        for index, num in enumerate(gameBoardString):
            enemyGameBoard[index] = num

# This function is used to convert your personal game board to a string which can be sent to your opponent
def convertGameBoardToString(gameBoard):
    return ''.join(map(str, gameBoard))

# This function is for testing purposes only
def printEnemyGameBoard():
    print('=' * 41)
    for i in range(0, len(enemyGameBoard), 10):
        print(' '.join(map(str, enemyGameBoard[i:i+10])))

def printGameBoard():
    print('=' * 55)
    print('        Your Board        |            Hits/Misses')
    print("   " + ' '.join(str(i) for i in range(1, 11)) + '   |       ' + ' '.join(str(i) for i in range(1, 11)))
    for i in range(0, len(personalGameBoard), 10):
        j = int(i / 10)
        leftCol = ' '.join(map(str, personalGameBoard[i:i+10]))
        rightCol = ' '.join(map(str, hitMissBoard[i:i+10]))
        print(f"{chr(65 + j)}  {leftCol}    |    {chr(65 + j)}  {rightCol}")

# Initial boat placement functions

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

    # For setup purposes
    if front == "" and back == "":
        return False
    
    if (not isValidMove(front) or not isValidMove(back)):
        print("Invalid boat")
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
    if valid == False:
        print("Invalid boat")
    return valid

def placeShip(front, back, boatLength, charType = None):
    if charType == None:
        charType = boatLength
    
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
                makeMove(front[0] + str(i + frontNum), personalGameBoard, charType)
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
                makeMove(chr(ord(frontChar) + i) + str(getMoveNumber(front)), personalGameBoard, charType)

def setupGamePieces():
    userInput = ""
    front = ""
    back = ""

    printGameBoard()
    while not isValidMove(userInput) or not isValidBoat(front, back, 5):
        print("Choose start and end points for your CARRIER (5 pegs)")
        userInput = input("Enter location of the bow (front) of the boat: ")
        front = userInput
        userInput = input("Enter location of the stern (back) of the boat: ")
        back = userInput
    placeShip(front, back, 5)
    printGameBoard()
    front = ""
    back = ""

    while not isValidMove(userInput) or not isValidBoat(front, back, 4):
        print("Choose start and end points for your BATTLESHIP (4 pegs)")
        userInput = input("Enter location of the bow (front) of the boat: ")
        front = userInput
        userInput = input("Enter location of the stern (back) of the boat: ")
        back = userInput
    placeShip(front, back, 4)
    printGameBoard()
    front = ""
    back = ""

    while not isValidMove(userInput) or not isValidBoat(front, back, 3):
        print("Choose start and end points for your CRUISER (3 pegs)")
        userInput = input("Enter location of the bow (front) of the boat: ")
        front = userInput
        userInput = input("Enter location of the stern (back) of the boat: ")
        back = userInput
    placeShip(front, back, 3)
    printGameBoard()
    front = ""
    back = ""

    while not isValidMove(userInput) or not isValidBoat(front, back, 3):
        print("Choose start and end points for your SUBMARINE (3 pegs)")
        userInput = input("Enter location of the bow (front) of the boat: ")
        front = userInput
        userInput = input("Enter location of the stern (back) of the boat: ")
        back = userInput
    placeShip(front, back, 3, monospace_digit_three)
    printGameBoard()
    front = ""
    back = ""

    while not isValidMove(userInput) or not isValidBoat(front, back, 2):
        print("Choose start and end points for your DESTROYER (2 pegs)")
        userInput = input("Enter location of the bow (front) of the boat: ")
        front = userInput
        userInput = input("Enter location of the stern (back) of the boat: ")
        back = userInput
    placeShip(front, back, 2)
    printGameBoard()

    print("Let the game begin!")

# Functions for making a move
def isCharAthruJ(char):
    return char.upper() in 'ABCDEFGHIJ'

def isChar1thru10(char):
    return char.isdigit() and 1 <= int(char) <= 10

def isValidMove(move):
    bool = (len(move) == 2 or len(move) == 3) and isCharAthruJ(move[0]) and isChar1thru10(move[1])

    if not bool and move != "":
        print("Invalid location")
    return bool

# makeMove returns the original move
def makeMove(move, gameBoard, charType = 'X'):
    if isValidMove(move):
        if len(move) == 2:
            moveIndex = ((ord(move[0].upper()) - 65) * 10) + (int(move[1]) - 1)
        else:
            moveIndex = ((ord(move[0].upper()) - 65) * 10) + 9 # Case that you chose 10

        if gameBoard[moveIndex] != '0':
            updateBoatLog(gameBoard[moveIndex]) # Parameter tells us which boat was hit
            hitMissBoard[moveIndex] = charType
            isGameOver(personalBoatLog, enemyBoatLog)
        else:
            hitMissBoard[moveIndex] = 'M'
        
        if charType != 'X':
            # Used during ship setup
            personalGameBoard[moveIndex] = charType
    else:
        print(move, " Is an invalid Move")
    return move

# (order: destroyer, submarine, cruiser, battleship, carrier)
def updateBoatLog(charType):
    if charType == '2':
        enemyBoatLog[0] -= 1
        if (enemyBoatLog[0] == 0):
            print("Enemy: You sunk my DESTROYER!")
        else:
            print("Enemy: You hit my DESTROYER!")
    elif charType == monospace_digit_three:
        enemyBoatLog[1] -= 1
        if (enemyBoatLog[1] == 0):
            print("Enemy: You sunk my SUBMARINE!")
        else:
            print("Enemy: You hit my SUBMARINE!")
    elif charType == '3':
        enemyBoatLog[2] -= 1
        if (enemyBoatLog[2] == 0):
            print("Enemy: You sunk my CRUISER!")
        else:
            print("Enemy: You hit my CRUISER!")
    elif charType == '4':
        enemyBoatLog[3] -= 1
        if (enemyBoatLog[3] == 0):
            print("Enemy: You sunk my BATTLESHIP!")
        else:
            print("Enemy: You hit my BATTLESHIP!")
    elif charType == '5':
        enemyBoatLog[4] -= 1
        if (enemyBoatLog[4] == 0):
            print("Enemy: You sunk my CARRIER!")
        else:
            print("Enemy: You hit my CARRIER!")
    else:
        print("Enemy: Miss!")

def isGameOver(personalLog, enemyLog):
    gameOver = False
    enemyWon = True
    youWon = True

    for boat in personalBoatLog:
        if boat != 0:
            enemyWon = False

    for boat in enemyBoatLog:
        if boat != 0:
            youWon = False

    if youWon:
        print("Enemy: Well played")
        print("YOU WIN!")
        gameOver = True
    elif enemyWon:
        print("Enemy: That was too easy")
        print("YOU LOSE")
        gameOver = True

    return gameOver

# example game play, albeit for only one person
def playGame(enemyBoardString):
    generateEnemyGameBoard(enemyBoardString)
    # you would then call processEnemyMove()

    setupGamePieces()

    while not isGameOver(personalBoatLog, enemyBoatLog):
        userInput = input("Make your move: ")
        makeMove(userInput, enemyGameBoard)
        printGameBoard()




# Testing
if __name__ == '__main__':
    playGame(sampleBoardString)

    # printEnemyGameBoard()
    # printGameBoard()

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
    # placeShip('a1', 'b1', 2)
    # placeShip('f10', 'j10', 5)