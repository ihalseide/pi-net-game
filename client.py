#### Battleship game client
#import game_common # module for common game code for the client and server
#import threading
import socket

# When sending "messages", this is how many bytes long the length field is
PREFIX_LENGTH = 5

def input_IP() -> str:
    while True:
        ip = input("Server IP address: ").strip()
        if not ip:
            print("Blank IP address value is invalid.")
            continue
        return ip

def input_port() -> int:
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
    
def send_message(sock: socket.socket, message: str):
    assert(PREFIX_LENGTH == 5)
    length = "{:0>5}".format(len(message))
    print(f"send_message (length={length})")
    sock.sendall(length.encode("utf-8"))
    sock.sendall(message.encode("utf-8"))

def recv_message(sock: socket.socket) -> str:
    try:
        length = sock.recv(PREFIX_LENGTH)
    except OSError:
        raise ValueError("could not receive response from connection")
    try:
        length_num = int(length)
    except ValueError:
        raise ValueError("connection sent invalid length")
    try:
        result = str(sock.recv(length_num))
    except OSError:
        raise ValueError("could not receive response from connection")
    return result
    
def join_game(sock: socket.socket) -> str|None:
    send_message(sock, "join")
    try:
        response = recv_message(sock)
    except:
        return None
    return response

# Get a user address until a connection can be established
def get_address_and_connect_socket() -> socket.socket:
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
            print(f"Could not establish connection to {server_ip} on port {port}")
            print("Re-enter IP address and port number to try again...")
            continue

def main() -> None:
    while True:
        sock = get_address_and_connect_socket()
        response = join_game(sock)
        if response is None:
            print("The server is not hosting a joinable game")
            sock.close()
            continue
        elif response == "yes":
            break
        else:
            print("The server is hosting a game and refused your request to join game (a game may already be running)")
            sock.close()
            continue
    print(f"Joined server! (response={response})")
    sock.close()

if __name__ == '__main__':
    main()