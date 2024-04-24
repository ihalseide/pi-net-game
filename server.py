#!/usr/bin/env python3

'''
Battleship game server
'''

import socket
import Battleship as bs

# The size in bytes of the length field when sending messages.
PREFIX_LENGTH: int = 5

def check_board(board: str) -> bool:
    '''
    This should probably be something that can be checked with the game api.
    Something to check whether the board the server has recieved is valid.
    This currently just accepts any board
    '''
    return True

def message_send(sock: socket.socket, message: str, do_log=True):
    '''
    Send a length-prefixed message string to the socket connection.
    This function is the counterpart to `message_recv`.
    Messages are in the form: [length field][data field]
    - where the length field is a fixed-length number string (like "00009")
    - where the data field is a string with length given by converting the length field to an integer
    '''
    assert(PREFIX_LENGTH == 5)
    length = "{:0>5}".format(len(message))
    if do_log: print(f'(message_send)"{length}{message}"')
    sock.sendall(length.encode())
    sock.sendall(message.encode())

def message_recv(sock: socket.socket, do_log=True) -> str:
    '''
    Receive a length-prefixed message string from the socket connection.
    This function is the counterpart to `message_send`.
    Messages are in the form: [length field][data field]
    - where the length field is a fixed-length number string (like "00009")
    - where the data field is a string with length given by converting the length field to an integer
    '''
    if do_log: 
        print("(message_recv)...")
    try:
        length_bytes = sock.recv(PREFIX_LENGTH)
        length_field = length_bytes.decode()
    except OSError:
        raise ValueError("could not receive response from connection")
    if len(length_field) == 0:
        raise ValueError("connection is closed")
    if (l := len(length_field)) != PREFIX_LENGTH:
        raise ValueError(f"the connection sent a length field which itself has an unexpected length of {l}")
    try:
        length_num = int(length_field)
    except ValueError:
        raise ValueError("the connection sent a length field which could not be converted to an integer value")
    if length_num <= 0:
        raise ValueError(f"the connection sent a non-positive integer in the length field: {length_num}")
    if do_log: 
        print(f"(message_recv){length_field}...")
    try:
        data_field = sock.recv(length_num, socket.MSG_WAITALL).decode()
    except OSError:
        raise ValueError("could not receive the full data response from the connection")
    if (actual_length := len(data_field)) != length_num:
        raise ValueError(f"connection indicated it would send {length_num} bytes, but {actual_length} bytes was actually received")
    return data_field

def accept_board(client_sock: socket.socket):
    '''
    Send an affermative to board setup, this may change depending on what network protocol we agree on
    '''
    message_send(client_sock, "setup_ok")

def deny_board(client_sock: socket.socket):
    '''
    Deny the recieved board setup, this may change depending on what network protocol we agree on
    '''
    message_send(client_sock, "setup_bad")

def accept_move(client_sock: socket.socket):
    '''
    Accept the recieved move, this may change depending on what network protocol we agree on
    '''
    message_send(client_sock, "move_ok")

def deny_move(client_sock: socket.socket):
    '''
    Deny the recieved move, this may change depending on what network protocol we agree on
    '''
    message_send(client_sock, "move_bad")

def get_move(client_sock: socket.socket):
    full_move = message_recv(client_sock)
    print(full_move[0:8])
    move = full_move[8:]
    return move

def player_turn(player: socket.socket):
    '''
    Inform the player it is their turn, and recieve their move
    this may change depending on what network protocol we agree on
    '''
    message_send(player, "your_turn")
    move = get_move(player)
    print("Move was: " + move)
    if bs.isValidMove(move):
        accept_move(player)
        # TODO: do something with the move, incl. telling the other player what it was
    else:
        deny_move(player)

def not_player_turn(player: socket.socket):
    '''
    Inform the player it isn't their turn, this may change depending on what network protocol we agree on
    '''
    message_send(player, "not_your_turn")

def get_player(sock: socket.socket):
    '''
    Get a player socket and address, and make sure they send the proper join message
    sock generally should be the socket the server is running on
    '''
    while True:
        print("listening...")
        (client_sock, client_addr) = sock.accept()
        print("got one!")
        try:
            m = message_recv(client_sock)
        except Exception as e:
            print(e)
            return None
        print(m)
        message_send(client_sock, "server_yes")
        if client_sock is not None and client_addr is not None:
            return client_sock, client_addr

def get_player_valid_board(sock: socket.socket):
    '''
    Get a player socket and address with get_player, then ensure they have a valid board
    Checking the board is valid will use the battleship game library
    Sends a message to the client if the setup is bad, and refuses connection (this may be changed later)
    '''
    while True:
        client_sock, client_addr = get_player(sock)
        board_received = message_recv(client_sock)
        if (check_board(board_received)):
            accept_board(client_sock)
            return client_sock, client_addr, board_received
        else:
            deny_board(client_sock)

def game_loop(p1: socket.socket,p2: socket.socket):
    '''
    The basic game loop, one player goes then the other, alternating.
    TODO: make this more robust for if a client disconnects, should probably return to starting state (looking for players)
    TODO: Should there be a game end condition in the game api, use that to end the game when the time comes
    '''
    turn: bool = True
    while True:
        if turn:
            player_turn(p1)
            not_player_turn(p2)
        else:
            player_turn(p2)
            not_player_turn(p1)
        turn = not turn

def main() -> None:
    sock = socket.create_server(('localhost', 7777), family=socket.AF_INET, backlog=1)
    p1_sock, p1_addr, p1_board = get_player_valid_board(sock)
    p2_sock, p2_addr, p2_board = get_player_valid_board(sock)
    game_loop(p1_sock, p2_sock)

if __name__ == '__main__':
    main()