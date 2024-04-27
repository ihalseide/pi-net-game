#!/usr/bin/env python3

'''
Battleship game server
'''

import socket
import Battleship as bs
from NetMessage import *

p1_sock, p1_addr, p1_board, p1_board_2, p2_sock, p2_addr, p2_board, p2_board_2 = None, None, None, None, None, None, None, None

def accept_connection(client_sock: socket.socket):
    '''
    Send an affermative to board setup, this may change depending on what network protocol we agree on
    '''
    message_send(client_sock, MSG_ACCEPT)

def hit_move(client_sock: socket.socket):
    '''
    Accept the recieved move, this may change depending on what network protocol we agree on
    '''
    message_send(client_sock, f"{MSG_MOVE} hit")

def miss_move(client_sock: socket.socket):
    '''
    Deny the recieved move, this may change depending on what network protocol we agree on
    '''
    message_send(client_sock, f"{MSG_MOVE} miss")

def get_move(client_sock: socket.socket):
    full_move = message_recv(client_sock)
    print(full_move[0:len(MSG_MOVE)+1])
    move = full_move[len(MSG_MOVE)+1:]
    return move

def player_turn(player: socket.socket):
    '''
    Inform the player it is their turn, and recieve their move
    this may change depending on what network protocol we agree on
    '''
    message_send(player, MSG_MY_TURN)
    try:
        move = get_move(player)
        print("Move was: " + move)
        if bs.isValidMove(move):
            # TODO: do something with the move, incl. telling the other player what it was
            # for now just says that it missed because there isn't a good way for the server side to deal with the library's methods
            message_send(player, f"{MSG_OUTCOME} miss")
        else:
            message_send(player, f"{MSG_OUTCOME} invalid")
    except Exception as e:
        # TODO: handle a player disconnected gracefully, or at least semi-gracefully here
        pass 

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
            print(m)
            return client_sock, client_addr, m
        except Exception as e:
            print(e)
            return None

def get_player_empty_board(sock: socket.socket):
    '''
    Get a player socket and address with get_player, then ensure they have a valid board
    Checking the board is valid will use the battleship game library
    Sends a message to the client if the setup is bad, and refuses connection (this may be changed later)
    '''
    while True:
        client_sock, client_addr, m = get_player(sock)
        if (client_sock is None or client_addr is None or m is None):
            return None, None, None
        board_received = m[len(MSG_JOIN)+1:]
        print(board_received)
        accept_connection(client_sock)
        return client_sock, client_addr, board_received

def game_loop(p1: socket.socket,p2: socket.socket):
    '''
    The basic game loop, one player goes then the other, alternating.
    TODO: make this more robust for if a client disconnects, should probably return to starting state (looking for players)
    TODO: Should there be a game end condition in the game api, use that to end the game when the time comes
    '''
    turn: bool = True
    while True:
        if turn:
            personalGameBoard = p1_board
            enemyGameBoard = p2_board
            player_turn(p1)
        else:
            personalGameBoard = p2_board
            enemyGameBoard = p1_board
            player_turn(p2)
        turn = not turn

def recieve_board(player: socket.socket):
    try:
        board1 = message_recv(player)
        board2 = message_recv(player)
        print(board1, "\n", board2)
        return board1, board2
    except Exception as e:
        print(e)
        return None, None

def main() -> None:
    sock = socket.create_server(('localhost', 7777), family=socket.AF_INET, backlog=1)
    global p1_sock, p1_addr, p1_board, p1_board_2, p2_sock, p2_addr, p2_board, p2_board_2
    """ Handle player joining once the client sends the board state
    while p1_board_2 is None:
        p1_sock, p1_addr, p1_board = get_player_empty_board(sock)
        p1_board, p1_board_2 = recieve_board(p1_sock)
    while p2_board_2 is None:
        p2_sock, p2_addr, p2_board = get_player_empty_board(sock)
        p2_board, p2_board_2 = recieve_board(p2_sock)
    """
    while p1_sock is None:
        p1_sock, p1_addr, p1_board = get_player_empty_board(sock)
    while p2_sock is None:
        p2_sock, p2_addr, p2_board = get_player_empty_board(sock)
    game_loop(p1_sock, p2_sock)

if __name__ == '__main__':
    main()
