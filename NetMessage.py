'''
Common network code for the Battleship client and server.
'''

import socket

## When sending network messages, this is how many bytes long the `length field` is.
## NOTE: this will change based on what we agree on for the net protocol.
LENGTH_PREFIX_LENGTH: int = 5

def message_send(sock: socket.socket, message: str, do_log=True):
    '''
    Send a length-prefixed message string to the socket connection.
    This function is the counterpart to `message_recv`.
    Messages are in the form: [length field][data field]
    - where the length field is a fixed-length number string (like "00009")
    - where the data field is a string with length given by converting the length field to an integer
    '''
    length = len(message)
    assert(LENGTH_PREFIX_LENGTH == 5) # If this assertion is incorrect, then update this line and the next one.
    length_field = "{:0>5}".format(length)
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
        print(f"(message_recv {LENGTH_PREFIX_LENGTH})...")
    try:
        length_field = sock.recv(LENGTH_PREFIX_LENGTH, socket.MSG_WAITALL)
    except OSError:
        raise ValueError("could not receive response from connection")
    length_str = length_field.decode()
    if len(length_str) == 0:
        raise OSError("connection is closed")
    if (l := len(length_str)) != LENGTH_PREFIX_LENGTH:
        raise ValueError(f"the connection sent a length field which itself has an unexpected length of {l}")
    try:
        length_num = int(length_str)
    except ValueError:
        raise ValueError("the connection sent a length field which could not be converted to an integer value")
    if length_num <= 0:
        raise ValueError(f"the connection sent a non-positive integer in the length field: {length_num}")
    if do_log: 
        print(f"(message_recv){length_str}...")
    try:
        data_field = sock.recv(length_num, socket.MSG_WAITALL)
    except OSError:
        raise ValueError("could not receive the full data response from the connection")
    if (actual_length := len(data_field)) != length_num:
        raise ValueError(f"connection indicated it would send {length_num} bytes, but {actual_length} bytes was actually received")
    return data_field.decode()