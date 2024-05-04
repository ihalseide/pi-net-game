#!/usr/bin/env python3

'''
Battleship game client.
This program is single-threaded.
'''

import Battleship as bs
from NetMessage import *
import socket
    
def message_send_join(sock: socket.socket, board: list[str]):
    '''
    Send a [join] message to the connection, with the initial board.
    '''
    board_str = bs.game_board_to_str(board)
    message_send(sock, f"{MSG_JOIN} {board_str}")

def get_user_move() -> str:
    '''
    Ask the local player for a square to try to hit on the opponent's board.
    '''
    return input("Enter your move (a square to guess): ").strip().lower()

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
    
def game_connect(board: list[str], server_ip: str, port: int, timeout_seconds: float = 0.5) -> socket.socket | str:
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0)
    sock.settimeout(timeout_seconds)
    sock.connect((server_ip, port))
    message_send_join(sock, board)
    response = message_recv(sock)
    if response == MSG_ACCEPT:
        return sock
    else:
        sock.close()
        return response

def ask_and_join_server(board: list[str]) -> socket.socket | None:
    ## Allow the user to keep trying to connect to servers over and over again.
    while True:
        ip = input_IP()
        port = input_port()
        try:
            result = game_connect(board, ip, port, timeout_seconds=1.0)
            if isinstance(result, str):
                print(f"Game server did not let you join, server sent: \"{result}\"")
            else:
                print("Successfully joined the server!")
                return result
        except OSError:
            print("Could not create a connection to that server")        

def client_game_loop(sock: socket.socket, board: list[str]) -> None:
    '''
    Main client game loop to keep sending moves whenever it is this client's turn.
    '''
    opponent_board = bs.create_board()
    opponent_ship_log = bs.create_ship_log(bs.CLASSIC_SHIPS)
    move_coord = '<invalid>'
    move_index = -1
    show_board = True
    invalid_msg_budget = 10
    while True:
        if show_board:
            bs.print_game_board(board, opponent_board)

        ## Get a Message from the server.
        try:
            msg = message_recv(sock)
        except (ValueError, OSError):
            ## Ignore up to a certain number of invalid messages
            invalid_msg_budget -= 1
            if invalid_msg_budget <= 0:
                print("The network connection is sending too many incomprehenible messages")
                break
            else:
                continue

        if msg == MSG_MY_TURN:
            ## Server sent that it is our turn to go
            while True:
                # Get valid move
                try:
                    move_coord = get_user_move()
                    move_index = bs.returnMoveIndex(move_coord)
                except ValueError:
                    print("Invalid move")
                    continue
                if opponent_board[move_index] in (bs.MISS_CHAR, bs.HIT_CHAR):
                    # Already guessed
                    print(f"You already guessed {move_coord.upper()}")
                    continue
                else:
                    break
            message_send(sock, f"{MSG_MOVE} {move_coord}")
            # get response in next loop (hit/miss)
            show_board = False

        elif msg == f"{MSG_OUTCOME} hit":
            ## Previously sent move was a hit
            assert(move_index >= 0)
            print(f"Your guess '{move_coord.upper()}' was a HIT!")
            opponent_board[move_index] = bs.HIT_CHAR
            show_board = True

        elif msg == f"{MSG_OUTCOME} miss":
            ## Previously sent move was a miss
            assert(move_index >= 0)
            print(f"Your guess '{move_coord.upper()}' was a MISS!")
            opponent_board[move_index] = bs.MISS_CHAR
            show_board = True

        elif msg.startswith(f"{MSG_OUTCOME} hit-sink"):
            ## Previously sent move was a hit, and that hit sinks an enemy ship.
            ## Message is: "<outcome> <hit-sink> <ship-name>"
            assert(move_index >= 0)
            ship_char = msg.split(maxsplit=2)[2]
            ship_name = 'ship'
            # Find ship name from character
            for _, s_name, s_char in bs.CLASSIC_SHIPS:
                if s_char == ship_char:
                    ship_name = s_name
                    break
            print(f"Your guess '{move_coord.upper()}' was a HIT and SUNK the opponent's {ship_name.upper()} (marked with '{ship_char}' characters)!")
            opponent_board[move_index] = bs.HIT_CHAR
            bs.decrement_boat_log(ship_char, opponent_ship_log)
            show_board = True

        elif msg.startswith(MSG_FINISHED):
            ## Server is ending/finishing the game
            ## Message is: "<finish> <outcome>"
            the_rest = msg.split(maxsplit=1)[1]
            if the_rest == MSG_FINISHED_LOSE:
                print("Game over: you LOST!")
            elif the_rest == MSG_FINISHED_WIN:
                print("Game over: you WON!")
                print("Closing connection to server.")
            else:
                print("Server is ending the game for some other reason.")
                print(f"Server sent: '{msg}'")
            # No more turns, done with this game loop!
            break
        
        elif msg.startswith(MSG_NOTE_GUESS):
            ## Server is sending the opponent's guess on our board.
            ## Message is: "<note> <coordinate>"
            the_coord = msg.split(maxsplit=1)[1]
            ## Add hit/miss mark to own board
            try:
                the_coord_index = bs.returnMoveIndex(the_coord)
            except ValueError:
                ## Ignore this message
                continue
            cell_val = board[the_coord_index]
            is_hit = (cell_val != bs.UNOCCUPIED) and (cell_val != bs.MISS_CHAR)
            hit_str = "HIT" if is_hit else "MISS"
            ## Update the cell to hit or miss unless it is already a hit or miss.
            if (cell_val != bs.MISS_CHAR) and (cell_val != bs.HIT_CHAR):
                hit_or_miss_char = bs.HIT_CHAR if is_hit else bs.MISS_CHAR
                board[the_coord_index] = hit_or_miss_char
            print(f"The opponent fired at your '{the_coord.upper()}' square, which was a {hit_str}.")
            show_board = True

        else:
            ## Other message
            print(f"Unhandled server message type.")
            print(f"Received server data: '{msg}'")
            show_board = False

def prompt_valid_board_location(board: list[str]) -> int:
    while True:
        x = input("\rEnter location for the ship's front (A1 through I10): ")
        try:
            index: int = bs.returnMoveIndex(x)
        except ValueError:
            print("\rCannot start placing a boat there: invalid location")
            continue
        if board[index] != bs.UNOCCUPIED:
            print("\rCannot start placing a boat there: spot out of range or already occupied")
            continue
        return index

def prompt_board_direction() -> str:
    while True:
        d = input("Enter direction for the ship to face, starting from the previous location. (u/d/l/r for Up, Down, Left, or Right): ")
        if not d:
            print("Cannot be empty")
            continue
        d = d.lower()[0]
        if d in 'udlr':
            return d
        else:
            print("Please enter [u]p, [d]own, [l]eft, or [r]ight")

def prompt_valid_board_direction(board: list[str], front_loc: int, length: int) -> str:
    while True:
        d_in = prompt_board_direction()
        row_0, col_0 = bs.index_to_row_col(front_loc)
        delta_row, delta_col = bs.direction_to_row_col_delta(d_in)
        ## Make sure each square following in the direction is valid.
        valid = True
        for i in range(length):
            row = row_0 + i * delta_row
            col = col_0 + i * delta_col
            if (not (0 <= row <= 9)) or (not (0 <= col <= 9)):
                ## Make sure no part of the ship goes off the board.
                valid = False
                direction = bs.direction_name(d_in)
                print(f"Ship cannot be layed out in the '{direction}' direction because the ship would go off the edge")
                break
            if board[bs.row_col_to_index(row, col)] != bs.UNOCCUPIED:
                ## Make sure no part of the ship goes over a non-blank part of the board.
                valid = False
                coord = bs.row_col_to_coord(row, col)
                direction = bs.direction_name(d_in)
                print(f"Ship cannot be layed out in the '{direction}' direction because there is an obstacle at {coord}")
                break
        if valid:
            return d_in

def player_setup_board(ships_info_tuple: tuple[tuple[int, str, str], ...]) -> list[str]:
    board = bs.create_board()
    dummy_hit_miss = bs.create_board(fill_value=' ')
    for (ship_length, ship_name, ship_value) in ships_info_tuple:
        bs.print_game_board(board, dummy_hit_miss)
        print(f"Place your {ship_name} (which occupies {ship_length} tiles)")
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
        bs.game_board_place_ship(board, front_loc, direction, ship_length, ship_value)
    bs.print_game_board(board, dummy_hit_miss)
    return board

def client_main() -> None:
    print("Welcome to the batship game client")
    try:
        while True:
            print("\nSet up your board for a new game!\n")
            board = player_setup_board(bs.CLASSIC_SHIPS)
            print("\nJoin a game server with its internet address...\n")
            sock = ask_and_join_server(board)
            if sock is not None:
                try:
                    client_game_loop(sock, board)
                finally:
                    sock.close()
    except KeyboardInterrupt:
        pass
    except EOFError:
        print("reached end of input")

if __name__ == '__main__':
    client_main()