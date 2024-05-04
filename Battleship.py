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

def create_board(fill_value: str = UNOCCUPIED) -> list[str]:
    return [ fill_value for _ in range(NUM_ROWS * NUM_COLS) ]

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

def replacer(a, b):
    '''Returns a one-argument function that will replace 'a' with 'b' '''
    return lambda x: b if x == a else x

def print_game_board(my_board: list[str], hit_miss_board: list[str]):
    print('=' * 55)
    print('        Your Board        |            Hits/Misses')
    print("   " + ' '.join(str(i) for i in range(1, 11)) + '   |       ' + ' '.join(str(i) for i in range(1, 11)))
    for i in range(0, len(my_board), 10):
        j = int(i / 10)
        leftCol = ' '.join(map(replacer(UNOCCUPIED, ' '), map(str, my_board[i:i+10])))
        rightCol = ' '.join(map(replacer(UNOCCUPIED, ' '), map(str, hit_miss_board[i:i+10])))
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


def index_to_row_col(index: int) -> tuple[int, int]:
    if index > 100:
        raise ValueError("index out of range")
    r = index // 10
    c = index % 10
    return r, c

def row_col_to_index(row: int, col: int) -> int:
    return row * 10 + col

def row_col_to_coord(row: int, col: int) -> str:
    if (not (0 <= row <= 9)):
        raise ValueError(f"invalid row value: {row}")
    if (not (0 <= col <= 9)):
        raise ValueError(f"invalid column value: {col}")
    return 'ACDEFGHIJ'[row] + str(col)

def direction_name(direction: str) -> str:
    names = {
        'u': 'up',
        'd': 'down',
        'l': 'left',
        'r': 'right',
    }
    return names[direction]

def direction_to_row_col_delta(direction: str) -> tuple[int, int]:
    # maps directions to delta_row, delta_column
    row_col_delta = {
        'u': (-1, 0),
        'd': (1, 0),
        'l': (0, -1),
        'r': (0, 1),
    }
    return row_col_delta[direction]

def game_board_place_ship(game_board: list[str], front_loc: int, direction: str, length: int, ship_char: str):
    row_0, col_0 = index_to_row_col(front_loc)
    delta_row, delta_col = direction_to_row_col_delta(direction)
    for i in range(length):
        row = row_0 + i * delta_row
        col = col_0 + i * delta_col
        game_board[row_col_to_index(row, col)] = ship_char

# Testing
if __name__ == '__main__':
    pass