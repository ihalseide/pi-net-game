#!/usr/bin/env python3

'''
Battleship game client
'''

import Battleship as bs
from NetMessage import *
import socket

# File path of where to store a IP address and port information for a connection.
ADDRESS_FILE_PATH: str = "server.txt"
    
def message_send_join(sock: socket.socket):
    '''
    Send a [join] message to the connection.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    message_send(sock, "join")

def join_game(sock: socket.socket) -> str|None:
    '''
    Send a request to join a server's game and get the response.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    message_send_join(sock)
    try:
        return message_recv(sock)
    except Exception as e:
        print('EXCEPTION WHILE JOINING', e)
        return None

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

def str_server_join_accept_p(s: str) -> bool:
    '''
    Predicate function for if a server response indicates that it accepts the client's join request.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    return s == "server_yes"

def str_server_my_turn_p(s: str) -> bool:
    '''
    Predicate function for if a server response indicates that it is the clients turn to make a move.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    return s == "your_turn"

def str_server_ok_move_p(s: str) -> bool:
    '''
    Predicate function for if a server response indicates that the previously sent move is ok with the server.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    return s == "move_ok"

def str_server_setup_ok_p(s: str) -> bool:
    '''
    Get if the previously sent board setup is ok from the server.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    return s == "setup_ok"

def send_setup(sock: socket.socket, board: str):
    '''
    Send a board setup request to the server.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    message_send(sock, f"board_setup {board}")

def recv_setup_ok(sock: socket.socket) -> bool:
    '''
    Receive response from server and see if it indicates that setup was ok.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    msg = message_recv(sock)
    return str_server_ok_move_p(msg)

def agree_setup(sock: socket.socket, board: str) -> bool:
    '''
    Send a setup to the connection and return whether the connection replies with a message that indicates the setup was approved.
    '''
    send_setup(sock, board)
    response = message_recv(sock)
    return str_server_setup_ok_p(response)

def agree_move(sock: socket.socket, move: str) -> bool:
    '''
    Send a move and get if it is accepted by the server.
    '''
    send_move(sock, move)
    resp = message_recv(sock)
    return str_server_ok_move_p(resp)

def send_move(sock: socket.socket, move: str):
    '''
    Send a game client move to be made to the server socket.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    message_send(sock, f"do_move {move}")

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
        response = join_game(sock)
        if response is None:
            print("The server is not hosting a joinable game")
            sock.close()
            continue
        elif str_server_join_accept_p(response):
            ## Successfully joined
            break
        else:
            print("The requested server is hosting a game and refused your request to join game (a game may already be running)")
            sock.close()
            continue
    print(f"Joined server! (response={response})")
    test_board_layout = read_file("fixedBoard.txt").decode()
    if not agree_setup(sock, test_board_layout):
        # For now, give up
        sock.close()
        print("server denied the board")
        return
    while True:
        # Loop to forever keep sending moves when it is this client's turn.
        msg = message_recv(sock)
        if not str_server_my_turn_p(msg):
            print(f"Not my turn")
            print(f"server sent: \"{msg}\"")
            continue
        move = get_user_move()
        print(f"move: {move}")
        if not agree_move(sock, move):
            print(f"Invalid move")
            print(f"server sent: \"{msg}\"")
            break
    sock.close()
    print("Goodbye from the game client")

if __name__ == '__main__':
    client_main()