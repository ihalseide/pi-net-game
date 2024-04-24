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

## Network message types -- based what the a message starts with (the prefix).
## NOTE: this will change based on what we agree on for the net protocol.
MSG_JOIN = "join" # from client to server
MSG_MOVE = "move" # from client to server
MSG_OUTCOME = "outcome" # from server to client
MSG_MY_TURN = "turn" # from server to client
MSG_ACCEPT = "accept" # from server to client
MSG_FINISHED = "finish" # from server to client
MSG_FINISHED_LOSE = "lose" # second part of the MSG_FINISHED message
MSG_FINISHED_WIN = "win" # second part of the MSG_FINISHED message
    
def message_send_join(sock: socket.socket, board: str):
    '''
    Send a [join] message to the connection.
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
    
def stamp_file(file_path: str, contents: bytes) -> int:
    '''Overwrite a file at `file_path` with `contents`.'''
    with open(file_path, 'wb') as f:
        return f.write(contents)
    
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
    
def save_address(ip: str, port: int, file_path: str = ADDRESS_FILE_PATH):
    '''
    Save a IP:port value to a fixed file.
    '''
    data = f"{ip}\n{port}\n"
    stamp_file(file_path, data.encode())

def client_loop(sock: socket.socket) -> None:
    '''
    Main client game loop to keep sending moves whenever it is this client's turn.
    '''
    while True:
        msg = message_recv(sock)
        if msg == MSG_MY_TURN:
            ## Server sent that it is our turn to go
            move = get_user_move()
            print(f"move: {move}")
            send_move(sock, move)
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

def client_main() -> None:
    print("Welcome to the game client")
    while True:
        # Loop to forever keep getting server addresses to try and join.
        try:
            # Create socket and save a successful connection to a file
            ip, port, sock = get_address_and_connect_socket()
            print('INFO', ip, port, sock)
            save_address(ip, port)
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            return
        message_send_join(sock, bs.convertGameBoardToString(bs.gameBoard))
        response = message_recv(sock)
        if response is None:
            print("The server is not hosting a joinable game")
            sock.close()
            continue
        elif response == MSG_ACCEPT:
            ## Successfully joined
            break
        else:
            print("The requested server is hosting a game and refused your request to join game (a game may already be running)")
            sock.close()
            continue
    print(f"Joined server! (response={response})")
    client_loop(sock)
    sock.close()
    print("Goodbye from the game client")

if __name__ == '__main__':
    client_main()