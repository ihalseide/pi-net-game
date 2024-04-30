#!/usr/bin/env python3

'''
Battleship game server
'''

import socket
import Battleship as bs
from NetMessage import *

p1_sock, p1_addr, p1_board, p1_board_hm, p2_sock, p2_addr, p2_board, p2_board_hm = None, None, None, None, None, None, None, None
p1_boatLog = [2, 3, 3, 4, 5] 
p2_boatLog = [2, 3, 3, 4, 5]
sock = None

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
            move_ind = bs.returnMoveIndex(move)
            target = bs.enemyGameBoard[move_ind]
            if target != '0' and target != 'X':
                bs.updatePersonalBoatLog(target, bs.enemyBoatLog)
                bs.enemyGameBoard[move_ind] = 'X'
                message_send(player, f"{MSG_OUTCOME} hit")
            else: message_send(player, f"{MSG_OUTCOME} miss")
        else:
            player_turn(player)
    except Exception as e:
        print(e)
        main()

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
            return None, None, None

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
        board_received = list(m[len(MSG_JOIN)+1:]) 
        print(board_received)
        accept_connection(client_sock)
        return client_sock, client_addr, board_received

def game_loop(p1: socket.socket,p2: socket.socket):
    '''
    The basic game loop, one player goes then the other, alternating.
    TODO: Should there be a game end condition in the game api, use that to end the game when the time comes
    '''
    turn: bool = True
    while True:
        if turn:
            bs.personalGameBoard = p1_board
            bs.enemyGameBoard = p2_board
            bs.personalBoatLog = p1_boatLog
            bs.enemyBoatLog = p2_boatLog
            player_turn(p1)
            if bs.isGameOver(bs.personalBoatLog, bs.enemyBoatLog):
                if (lost(enemyBoatLog)):
                    message_send(p1, f"{MSG_FINISHED} {MSG_FINISHED_WIN}")
                    message_send(p2, f"{MSG_FINISHED} {MSG_FINISHED_LOSE}")
                    main()
        else:
            bs.personalGameBoard = p2_board
            bs.enemyGameBoard = p1_board
            bs.personalBoatLog = p2_boatLog
            bs.enemyBoatLog = p1_boatLog
            player_turn(p2)
            if bs.isGameOver(bs.personalBoatLog, bs.enemyBoatLog):
                if (lost(enemyBoatLog)):
                    message_send(p2, f"{MSG_FINISHED} {MSG_FINISHED_WIN}")
                    message_send(p1, f"{MSG_FINISHED} {MSG_FINISHED_LOSE}")
                    main()
        turn = not turn

def is_lost(boatLog):
    lost = True
    for boat in boatLog:
        if boat != 0:
            lost = False
    return lost

def cleanup_between():
    try:
        p1_sock.close()
    except Exception as e:
        print(e)
    try: 
        p2_sock.close()
    except Exception as e:
        print(e)

def main() -> None:
    global sock
    if sock == None:
        sock = socket.create_server(('localhost', 7777), family=socket.AF_INET, backlog=1)
    else:
        cleanup_between()
    global p1_sock, p1_addr, p1_board, p2_sock, p2_addr, p2_board, p1_boatLog, p2_boatLog
    p1_sock = None
    p2_sock = None
    p1_boatLog = [2, 3, 3, 4, 5] 
    p2_boatLog = [2, 3, 3, 4, 5] 
    while p1_sock is None:
        p1_sock, p1_addr, p1_board = get_player_empty_board(sock)
    while p2_sock is None:
        p2_sock, p2_addr, p2_board = get_player_empty_board(sock)
    game_loop(p1_sock, p2_sock)

if __name__ == '__main__':
    main()
