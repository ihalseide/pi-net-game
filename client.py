#!/usr/bin/env python3

'''
Battleship game client
'''

#import game_common # placeholder name of our module for common game code for the client and server
import socket

# When sending network messages, this is how many bytes long the length field is
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
        return port_num
    
def message_send(sock: socket.socket, message: str):
    '''Send a length-prefixed message string to the socket connection.'''
    assert(PREFIX_LENGTH == 5)
    length = "{:0>5}".format(len(message))
    print(f"send_message (length={length})")
    sock.sendall(length.encode("utf-8"))
    sock.sendall(message.encode("utf-8"))

def message_recv(sock: socket.socket, do_log=True) -> str:
    '''Receive a length-prefixed message string from the socket connection.'''
    if do_log: print("awaiting message length from connection...")
    try:
        length_field = sock.recv(PREFIX_LENGTH)
    except OSError:
        raise ValueError("could not receive response from connection")
    if len(length_field) != PREFIX_LENGTH:
        raise ValueError("the connection sent a length field which itself has the wrong length")
    try:
        length_num = int(length_field)
    except ValueError:
        raise ValueError("the connection sent an invalid length value")
    if do_log: print("awaiting message data from connection...")
    try:
        data_field = str(sock.recv(length_num))
    except OSError:
        raise ValueError("could not receive the full data response from the connection")
    return data_field
    
def message_send_join(sock: socket.socket):
    '''
    Send a [join] message to the connection.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    message_send(sock, "join")

def join_game(sock: socket.socket) -> str|None:
    '''Send a request to join a server's game and get the response.'''
    message_send_join(sock)
    try:
        return message_recv(sock)
    except:
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

def str_server_is_ok_move(s: str) -> bool:
    '''
    Predicate function for if a server response indicates that the previously sent move is ok with the server.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    return s == "move_ok"

def recv_is_setup_ok(sock: socket.socket) -> bool:
    '''
    Get if the previously sent board setup is ok from the server.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    return str_server_is_ok_move(message_recv(sock))

def send_setup(sock: socket.socket, board: str):
    '''NOTE: this will change based on what we agree on for the net protocol.'''
    message_send(sock, f"board_setup {board}")

def agree_setup(sock: socket.socket, board: str) -> bool:
    send_setup(sock, board)
    return recv_is_setup_ok(sock)

def agree_move(sock: socket.socket, move: str) -> bool:
    '''
    Send a move and get if it is accepted by the server.
    '''
    send_move(sock, move)
    msg = message_recv(sock)
    return str_server_is_ok_move(msg)

def send_move(sock: socket.socket, move: str):
    '''
    Send a game client move to be made to the server socket.
    NOTE: this will change based on what we agree on for the net protocol.
    '''
    message_send(sock, f"do_move {move}")

def get_user_move() -> str:
    raise NotImplementedError("not yet")

def read_file(file_path: str) -> bytes:
    '''Read a whole file.'''
    with open(file_path, 'rb') as f:
        return f.read()

def main() -> None:
    fixed_board = read_file("fixedBoard.txt").decode('utf-8')
    print(fixed_board)
    print("Welcome to the game client")
    while True:
        # Loop to forever keep getting server addresses to try and join.
        try:
            sock = get_address_and_connect_socket()
        except KeyboardInterrupt:
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
            print("The server is hosting a game and refused your request to join game (a game may already be running)")
            sock.close()
            continue
    print(f"Joined server! (response={response})")
    if not agree_setup(sock, fixed_board):
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