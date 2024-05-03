'''
Common network code for the Battleship client and server.
'''

import socket

## When sending network messages, this is how many bytes long the `length field` is.
## NOTE: this will change based on what we agree on for the net protocol.
LENGTH_PREFIX_LENGTH: int = 5

## Network message types -- based what the a message starts with (the prefix).
## NOTE: this will change based on what we agree on for the net protocol.
MSG_JOIN = "j" # from client to server: request to join. No arguments.
MSG_MOVE = "m" # from client to server. Takes argument: the board position to guess.
MSG_OUTCOME = "o" # from server to client: response to a move message. Takes argument: "hit", "miss", or "hit-sink "<coordinate>
MSG_MY_TURN = "t" # from server to client. No arguments.
MSG_ACCEPT = "a" # from server to client: accept connection.
MSG_FINISHED = "f" # from server to client: game over. Takes argument: win/lose (see next lines below).
MSG_FINISHED_LOSE = "l" # second part of the MSG_FINISHED message
MSG_FINISHED_WIN = "w" # second part of the MSG_FINISHED message
MSG_NOTE_GUESS = "ng" # from server to client: inform client of a guess from the other client (opponent move). Takes argument: the board position.

def message_send(sock: socket.socket, message: str):
    '''
    Send a length-prefixed message string to the socket connection.
    This function is the counterpart to `message_recv`.
    Messages are in the form: [length field][data field]
    - where the length field is a fixed-length number string (like "00009")
    - where the data field is a string with length given by converting the length field to an integer
    '''

    message_bytes = message.encode()
    length = len(message_bytes)

    assert(LENGTH_PREFIX_LENGTH == 5) # If this assertion is incorrect, then update this line and the next one.
    length_field = "{:0>5}".format(length)
    
    length_bytes = length_field.encode()
    assert(len(length_bytes) == LENGTH_PREFIX_LENGTH)

    sock.sendall(length_bytes)
    sock.sendall(message_bytes)

def message_recv(sock: socket.socket) -> str:
    '''
    Receive a length-prefixed message string from the socket connection.
    This function is the counterpart to `message_send`.
    Messages are in the form: [length field][data field]
    - where the length field is a fixed-length number string (like "00009")
    - where the data field is a string with length given by converting the length field to an integer
    '''
    length_field = sock.recv(LENGTH_PREFIX_LENGTH, socket.MSG_WAITALL)
    if not length_field:
        raise ValueError("connection is closed")
    if (l := len(length_field)) != LENGTH_PREFIX_LENGTH:
        raise ValueError(f"the connection sent a length field which itself has an unexpected length of {l}")
    length_str = length_field.decode()
    try:
        length_num = int(length_str)
    except ValueError:
        raise ValueError(f"the connection sent a length field which could not be converted to an integer value: \"{length_str}\"")
    if length_num <= 0:
        raise ValueError(f"the connection sent a non-positive integer in the length field: {length_num}")
    data_field = sock.recv(length_num, socket.MSG_WAITALL)
    if (actual_length := len(data_field)) != length_num:
        raise ValueError(f"connection indicated it would send {length_num} bytes, but {actual_length} bytes was actually received")
    result = data_field.decode()
    return result