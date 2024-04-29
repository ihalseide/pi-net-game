#!/usr/bin/env python3

'''
Battleship game client.
This proram is single-threaded.
'''

import Battleship as bs
from NetMessage import *
import socket

## File path of where to store a IP address and port information for a connection.
ADDRESS_FILE_PATH: str = "server.txt"

## Unoccupied tile value.
UNOCCUPIED = '0'

# Collection of tuples where each entry is:
# (length, name, character) for the ship
STANDARD_SHIPS = (
    (2, 'destroyer', '2'), 
    (3, 'submarine', '3'), 
    (3, 'cruiser', bs.monospace_digit_three), 
    (4, 'battleship', '4'), 
    (5, 'carrier', '5'),
)

def print_my_board(personalGameBoard: list[str]) -> None:
    game_board_str = '=' * 22 + '\n'
    game_board_str += '        Your Board        |\n'
    game_board_str += "   " + ' '.join(str(i) for i in range(1, 11)) + '   |\n'
    
    for i in range(0, len(personalGameBoard), 10):
        j = int(i / 10)
        left_col = ' '.join(map(str, personalGameBoard[i:i+10]))
        game_board_str += f"{chr(65 + j)}  {left_col}    |\n"
    
    print(game_board_str)
    
def message_send_join(sock: socket.socket, board: str):
    '''
    Send a [join] message to the connection, with the initial board.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    message_send(sock, f"{MSG_JOIN} {board}")

def get_address_and_connect_socket() -> tuple[str, int, socket.socket]:
    '''Get a user address until a connection can be established'''
    family = socket.AF_INET # use IPv4
    kind = socket.SOCK_STREAM # use TCP
    ## Get first IP input.
    saved_server_ip = input_IP()
    first_loop = True
    while True:
        if first_loop:
            ## Use the first-entered saved IP
            server_ip = saved_server_ip
            first_loop = False
        else:
            ## Get new IP address or re-use old value
            server_ip = input("Enter new server IP (or leave blank to use previous value): ")
            if not server_ip:
                print(f"(Reusing previous IP value of \"{saved_server_ip}\")")
                server_ip = saved_server_ip
        ## Validate IP address.
        try:
            socket.inet_pton(family, server_ip)
        except OSError:
            print(f"IP address \"{server_ip}\" is invalid.")
            continue
        ## Save ip address for next time and get port.
        saved_server_ip = server_ip
        port = input_port()
        try:
            sock = socket.socket(family=family, type=kind, proto=0)
            sock.connect((server_ip, port))
            return server_ip, port, sock
            #return socket.create_connection((server_ip, port), timeout=2) # uses TCP
        except:
            print(f"Connection request timed out. Could not establish connection to {server_ip} on port {port}")
            print("Re-enter IP address and port number to try again...")
            continue

def send_move(sock: socket.socket, move: str):
    '''
    Send a game client move to be made to the server socket.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    message_send(sock, f"{MSG_MOVE} {move}")

def get_user_move() -> str:
    '''
    Ask the local player for a square to try to hit on the opponent's board.
    '''
    while True:
        ans = input("Enter your move (a square to guess): ").strip().lower()
        if not bs.isValidMove(ans):
            print(f"Try again, \"{ans}\" is not a valid move.")
        return ans

def read_file(file_path: str) -> bytes:
    '''Read and return all of the contents of the file at `file_path`.'''
    with open(file_path, 'rb') as f:
        return f.read()
    
## Quick temporary implementation of this function.
## TODO: make this better.
def display_board(board: str):
    lines = board.split()
    assert(len(lines) == 10)
    print(end=" ")
    for i in range(10):
        print(end=f"{1+i: >3}")
    print()
    print('-'*32)
    for i in range(10):
        line = lines[i]
        assert(len(line) == 10)
        letter = "ABCDEFGHIJ"[i]
        print(end=f"{letter}| ")
        for j in range(10):
            print(line[j], end='  ')
        print()

def input_IP() -> str:
    '''
    Get a IP address from the local user.
    '''
    while True:
        ip = input("Server IP address: ").strip()
        if not ip:
            print("Blank IP address value is invalid.")
            continue
        return ip

def input_port() -> int:
    '''
    Get a port number from the local user.
    '''
    while True:
        port = input("Server port number: ").strip()
        try:
            port_num = int(port)
        except ValueError:
            print("Please enter a valid integer value for the port number.")
            continue
        if port_num < 0:
            print("Please enter a non-negative value for the port number.")
            continue
        if port_num >= (2**16):
            print("Please enter a port number value that is less than 2^16.")
            continue
        return port_num

def client_connect_server(board: list[str]) -> socket.socket:
    board_str = ''.join(board)
    while True:
        # Loop to forever keep getting server addresses to try and join.
        try:
            # Create socket and save a successful connection to a file
            ip, port, sock = get_address_and_connect_socket()
            print('INFO', ip, port, sock)
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            exit(1)
        message_send_join(sock, board_str)
        response = message_recv(sock)
        if response is None:
            ## Got no response, try again.
            print("The server is not hosting a joinable game")
            sock.close()
            continue
        elif response == MSG_ACCEPT:
            ## Successfully joined.
            return sock
        else:
            ## Server sent some other message
            print("The requested server is hosting a game and refused your request to join game (a game may already be running)")
            print(f"Server sent: '{response}'")
            sock.close()
            continue

def client_game_loop(sock: socket.socket, board: list[str]) -> None:
    '''
    Main client game loop to keep sending moves whenever it is this client's turn.
    '''
    hit_miss_board = [ '~' for i in range(100) ]
    move_index = -1
    while True:
        print("Waiting for your turn...")
        msg = message_recv(sock)
        if msg == MSG_MY_TURN:
            ## Server sent that it is our turn to go
            print(bs.createPrintableGameBoard(board, hit_miss_board))
            move = get_user_move()
            move_index = bs.returnMoveIndex(move)
            print(f"move: {move}, index: {move_index}")
            send_move(sock, move)
            # get response in next loop (hit/miss)
            continue
        elif msg == f"{MSG_OUTCOME} hit":
            ## Previously sent move was a hit
            hit_miss_board[move_index] = 'X'
        elif msg == f"{MSG_OUTCOME} miss":
            ## Previously sent move was a miss
            assert(move_index >= 0)
            hit_miss_board[move_index] = '.'
        elif msg.startswith(MSG_FINISHED):
            ## Server is ending/finishing the game
            ## Message is: "finish " followed by the outcome
            the_rest = msg.split(maxsplit=1)[1]
            if the_rest == MSG_FINISHED_LOSE:
                print("Game over, you lost.")
            elif the_rest == MSG_FINISHED_WIN:
                print("Game over, you")
                print("Closing connection to server.")
            else:
                print("Server is ending the game for some other reason.")
                print(f"Server sent: '{msg}'")
            return
        else:
            ## Other message
            print(f"Unhandled server message type.")
            print(f"Received server data: '{msg}'")

def prompt_valid_board_location(board: list[str]) -> int:
    while True:
        x = input("\rEnter location for the ship's front (A1 through I10): ")
        try:
            index: int = bs.returnMoveIndex(x)
        except ValueError:
            print("\rCannot start placing a boat there: invalid location")
            continue
        if board[index] != UNOCCUPIED:
            print("\rCannot start placing a boat there: spot out of range or already occupied")
            continue
        return index

def prompt_board_direction() -> str:
    while True:
        d = input("Enter direction for the ship to face, starting from the previous location. (Up, Down, Left, or Right): ")
        if not d:
            print("Cannot be empty")
            continue
        d = d.lower()[0]
        if d in 'udlr':
            return d
        else:
            print("Please enter u[p], d[own], l[eft], or r[ight]")

def index_to_row_col(index: int) -> tuple[int, int]:
    if index > 100:
        raise ValueError("index out of range")
    r = index // 10
    c = index % 10
    return r, c

def row_col_to_index(row: int, col: int) -> int:
    return row * 10 + col

def row_col_to_coord(row: int, col: int) -> str:
    return 'ACDEFGHIJ'[row] + str(col)

def direction_name(direction: str) -> str:
    names = {
        'u': 'up',
        'd': 'down',
        'l': 'left',
        'r': 'right',
    }
    return names[direction]

def direction_to_delta(direction: str) -> tuple[int, int]:
    # maps directions to delta_row, delta_column
    row_col_delta = {
        'u': (-1, 0),
        'd': (1, 0),
        'l': (0, -1),
        'r': (0, 1),
    }
    return row_col_delta[direction]

def prompt_valid_board_direction(board: list[str], front_loc: int, length: int) -> str:
    while True:
        d_in = prompt_board_direction()
        row_0, col_0 = index_to_row_col(front_loc)
        delta = direction_to_delta(d_in)
        valid = True
        for i in range(length):
            row = row_0 + i * delta[0]
            col = col_0 + i * delta[1]
            if board[row_col_to_index(row, col)] != UNOCCUPIED:
                valid = False
                coord = row_col_to_coord(row, col)
                direction = direction_name(d_in)
                print(f"Ship cannot be layed out in the {direction} direction because there is an obstacle at {coord}")
                break
        if valid:
            return d_in

def set_ship_squares(board: list[str], front_loc: int, direction: str, length: int, ship_value: str):
    row_0, col_0 = index_to_row_col(front_loc)
    delta = direction_to_delta(direction)
    for i in range(length):
        row = row_0 + i * delta[0]
        col = col_0 + i * delta[1]
        board[row_col_to_index(row, col)] = ship_value

def player_setup_board(ships_info_tuple: tuple[tuple[int, str, str], ...]) -> list[str]:
    board = [ UNOCCUPIED for i in range(100) ]
    dummy_hit_miss = [ ' ' for i in range(100) ]
    for (ship_length, ship_name, ship_value) in ships_info_tuple:
        print_my_board(board)
        print(f"Place your {ship_name} (occupies {ship_length} tiles)")
        # Loop and catch Ctrl-C for direction choice to allow the user to re-choose the 'front_loc' location
        # in case there is no valid direction for a chosen 'front_loc'.
        while True:
            front_loc = prompt_valid_board_location(board)
            try:
                direction = prompt_valid_board_direction(board, front_loc, ship_length)
                break
            except (KeyboardInterrupt, EOFError):
                print(f"Undoing the starting position for the {ship_name}...")
                continue
        set_ship_squares(board, front_loc, direction, ship_length, ship_value)
    print(bs.createPrintableGameBoard(board, dummy_hit_miss))
    return board

def client_main() -> None:
    print("Welcome to the game client")
    try:
        board = player_setup_board(STANDARD_SHIPS)
    except (KeyboardInterrupt, EOFError):
        print("Board set-up cancelled, so the game will not continue.")
        return
    sock = client_connect_server(board)
    print(f"Joined server!")
    client_game_loop(sock, board)
    sock.close()
    print("Goodbye from the game client")

if __name__ == '__main__':
    client_main()