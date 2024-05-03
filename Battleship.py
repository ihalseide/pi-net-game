NUM_ROWS, NUM_COLS = 10, 10

ALT_3 = "\U0001D7F9" # Alternate 3 

## Other tile values.
HIT_CHAR = 'X'
MISS_CHAR = '.'
UNOCCUPIED = '0'

# The classic ship inventory.
# Collection of tuples where each entry is:
# (length, name, character) for the ship
CLASSIC_SHIPS = (
    (2, 'destroyer', '2'), 
    (3, 'submarine', '3'), 
    (3, 'cruiser', ALT_3), 
    (4, 'battleship', '4'), 
    (5, 'carrier', '5'),
)

def create_board() -> list[str]:
    return [ UNOCCUPIED for _ in range(NUM_ROWS * NUM_COLS) ]

def create_ship_log(ships = CLASSIC_SHIPS) -> dict[str, int]:
    return { ship[1]: ship[0] for ship in ships }

def process_enemy_move(enemy_move: str, my_board: list[str], my_ship_log: dict[str, int]):
    if is_valid_coord(enemy_move):
        index = returnMoveIndex(enemy_move)
        square_val = my_board[index]
        if square_val != UNOCCUPIED:
            decrement_boat_log(square_val, my_ship_log)
            is_boat_log_destroyed(my_ship_log)

def decrement_boat_log(ship_char: str, boat_log: dict[str, int]) -> int:
    boat_log[ship_char] -= 1
    return boat_log[ship_char]

# This function is used to convert your personal game board to a string which can be sent to your opponent
def game_board_to_str(board: list[str]):
    return ''.join(map(str, board))

def print_game_board(my_board: list[str], hit_miss_board: list[str]):
    print('=' * 55)
    print('        Your Board        |            Hits/Misses')
    print("   " + ' '.join(str(i) for i in range(1, 11)) + '   |       ' + ' '.join(str(i) for i in range(1, 11)))
    for i in range(0, len(my_board), 10):
        j = int(i / 10)
        leftCol = ' '.join(map(str, my_board[i:i+10]))
        rightCol = ' '.join(map(str, hit_miss_board[i:i+10]))
        print(f"{chr(65 + j)}  {leftCol}    |    {chr(65 + j)}  {rightCol}")

def create_printable_game_board_str(my_board, hit_miss_board) -> str:
    game_board_str = '=' * 55 + '\n'
    game_board_str += '        Your Board        |            Hits/Misses\n'
    game_board_str += "   " + ' '.join(str(i) for i in range(1, 11)) + '   |       ' + ' '.join(str(i) for i in range(1, 11)) + '\n'
    
    for i in range(0, len(my_board), 10):
        j = int(i / 10)
        left_col = ' '.join(map(str, my_board[i:i+10]))
        right_col = ' '.join(map(str, hit_miss_board[i:i+10]))
        game_board_str += f"{chr(65 + j)}  {left_col}    |    {chr(65 + j)}  {right_col}\n"
    
    return game_board_str

# Functions for making a move
def is_A_through_J(char: str) -> bool:
    return char.upper() in 'ABCDEFGHIJ'

def is_1_through_10(char: str) -> bool:
    return char.isdigit() and 1 <= int(char) <= 10

def is_valid_coord(move: str) -> bool:
    return (len(move) == 2 or len(move) == 3) and is_A_through_J(move[0]) and is_1_through_10(move[1:])

def returnMoveIndex(move: str) -> int:
    if (is_valid_coord(move)):
        if len(move) == 2:
            moveIndex = ((ord(move[0].upper()) - 65) * 10) + (int(move[1]) - 1)
        else:
            moveIndex = ((ord(move[0].upper()) - 65) * 10) + 9 # Case that you chose 10
        return moveIndex
    else:
        raise ValueError("invalid move coordinate")

# makeMove returns the original move
def makeMove(move, gameBoard, hitMissBoard, charType = 'X'):
    if is_valid_coord(move):
        if len(move) == 2:
            moveIndex = ((ord(move[0].upper()) - 65) * 10) + (int(move[1]) - 1)
        else:
            moveIndex = ((ord(move[0].upper()) - 65) * 10) + 9 # Case that you chose 10

        if charType != 'X':
            # Used during ship setup
            gameBoard[moveIndex] = charType
            return

        if gameBoard[moveIndex] != '0':
            hitMissBoard[moveIndex] = charType
            
        else:
            hitMissBoard[moveIndex] = 'M'
            
    
    else:
        response = move + " Is an invalid move"
        return response
    return moveIndex

def is_boat_log_destroyed(boat_log: dict[str, int]) -> bool:
    for k, v in boat_log.items():
        if v > 0:
            return False
    return True

# Testing
if __name__ == '__main__':
    pass