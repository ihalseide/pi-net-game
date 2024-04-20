#!/usr/bin/env python3

'''
Battleship game client
'''

import Battleship as bs
import socket

# When sending network messages, this is how many bytes long the `length field` is.
# NOTE: this will change based on what we agree on for the net protocol.
PREFIX_LENGTH: int = 5

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
            print("Please enter a port number value htat is less than 2^16.")
            continue
        return port_num
    
def message_send(sock: socket.socket, message: str, do_log=True):
    '''
    Send a length-prefixed message string to the socket connection.
    This function is the counterpart to `message_recv`.
    Messages are in the form: [length field][data field]
    - where the length field is a fixed-length number string (like "00009")
    - where the data field is a string with length given by converting the length field to an integer
    '''
    assert(PREFIX_LENGTH == 5) # If this assertion is incorrect, then update this line and the next one.
    length_field = "{:0>5}".format(len(message))
    if do_log: print(f'(message_send)"{length_field}{message}"')
    sock.sendall(length_field.encode())
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
        print(e)
        return None

def get_address_and_connect_socket() -> socket.socket:
    '''Get a user address until a connection can be established'''
    family = socket.AF_INET # use IPv4
    while True:
        server_ip = input_IP()
        try:
            server_ip_num = socket.inet_pton(family, server_ip)
        except OSError:
            print(f"IP address \"{server_ip}\" is invalid.")
            continue
        port = input_port()
        try:
            return socket.create_connection((server_ip, port), timeout=2) # uses TCP
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
    # TODO: implement this
    raise NotImplementedError("player move not yet implemented")

def read_file(file_path: str) -> bytes:
    '''Read a whole file.'''
    with open(file_path, 'rb') as f:
        return f.read()
    
def display_board(board: str):
    lines = board.split()
    assert(len(lines) == 10)
    print(end=" ")
    for i in range(10):
        print(end=f"{1+i: >3}")
    print()
    print('-'*(10*3+2))
    for i in range(10):
        line = lines[i]
        assert(len(line) == 10)
        letter = "ABCDEFGHIJ"[i]
        print(end=f"{letter}| ")
        for j in range(10):
            print(line[j], end='  ')
        print()

def main() -> None:
    test_board_layout = read_file("fixedBoard.txt").decode()
    display_board(test_board_layout)
    print("Welcome to the game client")
    while True:
        # Loop to forever keep getting server addresses to try and join.
        try:
            sock = get_address_and_connect_socket()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            return
        response = join_game(sock)
        if response is None:
            print("The server is not hosting a joinable game")
            sock.close()
            continue
        elif str_server_join_accept_p(response):
            break
        else:
            print("The requested server is hosting a game and refused your request to join game (a game may already be running)")
            sock.close()
            continue
    print(f"Joined server! (response={response})")
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
        if not agree_move(sock, move):
            print(f"Invalid move")
            print(f"server sent: \"{msg}\"")
            break
    sock.close()
    print("Goodbye from the game client")

if __name__ == '__main__':
    main()